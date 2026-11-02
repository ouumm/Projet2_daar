"""Demarre l'import des livres, l'index et le graphe sans commandes manuelles.

Le fichier .initialisation_ok est conserve dans le volume corpus. Si l'import
est interrompu, le prochain lancement reprendra les livres manquants.
"""
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from books.models import Book
from search.models import Term


class Command(BaseCommand):
    help = "Prepare automatiquement le corpus, l'index et le graphe."

    def add_arguments(self, parser):
        parser.add_argument("--target", type=int, default=1700)

    def handle(self, *args, **opts):
        target = opts["target"]
        if target < 1664:
            raise CommandError("Le sujet demande au moins 1664 livres")

        marker = Path(settings.CORPUS_DIR) / ".initialisation_ok"
        count = Book.objects.count()
        if marker.exists() and count >= target and Term.objects.exists():
            self.stdout.write(f"[initialisation] Deja pret : {count} livres")
            return

        marker.unlink(missing_ok=True)
        if count < target:
            self.stdout.write(f"[initialisation] Import Gutenberg ({count}/{target})")
            call_command("ingest_gutenberg", target=target)

        count = Book.objects.count()
        if count < target:
            raise CommandError(f"Import incomplet : {count}/{target} livres")

        self.stdout.write("[initialisation] Construction de l'index")
        call_command("build_index")
        self.stdout.write("[initialisation] Construction du graphe et des centralites")
        call_command("build_graph")
        marker.write_text(f"{count} livres indexes\n", encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"[initialisation] Termine : {count} livres"))
