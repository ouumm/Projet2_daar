"""Construit l'index inverse (Posting) et le vocabulaire (Term) a partir du corpus.

Usage : python manage.py build_index [--min-count 2]
"""
from collections import Counter
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from books.models import Book
from search.models import Posting, Term
from search.tokenize import tokenize


class Command(BaseCommand):
    help = "Construit l'index inverse des livres."

    def add_arguments(self, parser):
        parser.add_argument("--min-count", type=int, default=2,
                            help="ignore les mots qui apparaissent moins de N fois dans un livre")

    def handle(self, *args, **opts):
        Posting.objects.all().delete()
        Term.objects.all().delete()
        vocab = set()
        for book in Book.objects.all():
            path = Path(settings.CORPUS_DIR) / book.text_path
            if not path.exists():
                self.stderr.write(f"fichier manquant : {path}")
                continue
            counts = Counter(tokenize(path.read_text(encoding="utf-8", errors="ignore")))
            rows = [Posting(term=t, book=book, count=c)
                    for t, c in counts.items() if c >= opts["min_count"]]
            Posting.objects.bulk_create(rows, batch_size=5000)
            vocab.update(r.term for r in rows)
            self.stdout.write(f"{book.gutenberg_id}: {len(rows)} termes")
        Term.objects.bulk_create([Term(term=t) for t in vocab], batch_size=5000)
        self.stdout.write(self.style.SUCCESS(f"Index construit : {len(vocab)} termes."))
