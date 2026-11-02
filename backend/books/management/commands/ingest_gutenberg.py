"""Construit le corpus : telecharge des livres depuis Project Gutenberg (via l'API Gutendex).

Usage : python manage.py ingest_gutenberg --target 1700 --languages en,fr
Chaque livre garde au moins MIN_WORDS mots (exigence du sujet : 10000).
"""
import re
import time
from pathlib import Path

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from books.gutenberg_http import get_with_retries

from books.models import Book

MIN_WORDS = 10_000
GUTENDEX = "https://gutendex.com/books/"
START = re.compile(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.S)
END = re.compile(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG.*", re.S)


def strip_gutenberg(text: str) -> str:
    m = START.search(text)
    if m:
        text = text[m.end():]
    return END.sub("", text)


class Command(BaseCommand):
    help = "Telecharge le corpus Gutenberg dans CORPUS_DIR et remplit la table Book."

    def add_arguments(self, parser):
        parser.add_argument("--target", type=int, default=1700)
        parser.add_argument("--languages", default="en,fr")

    def handle(self, *args, **opts):
        corpus = Path(settings.CORPUS_DIR)
        corpus.mkdir(parents=True, exist_ok=True)
        count = Book.objects.count()
        url = f"{GUTENDEX}?languages={opts['languages']}"
        # Une session conserve les connexions pendant les milliers de telechargements.
        with requests.Session() as session:
            self.import_pages(session, url, count, opts["target"], corpus)

    def import_pages(self, session, url, count, target, corpus):
        while url and count < target:
            try:
                # Gutendex peut etre lent : 90 s de lecture, avec 4 tentatives.
                response = get_with_retries(
                    session, url, timeout=(10, 90), attempts=4,
                    log=self.stderr.write,
                )
                data = response.json()
            except (requests.RequestException, ValueError) as exc:
                # Le script de demarrage relancera l'import automatiquement.
                raise CommandError(f"Gutendex inaccessible pour le moment : {exc}") from exc
            for item in data["results"]:
                if count >= target:
                    break
                if Book.objects.filter(gutenberg_id=item["id"]).exists():
                    continue
                txt_url = next((u for f, u in item["formats"].items()
                                if f.startswith("text/plain")), None)
                if not txt_url:
                    continue
                try:
                    raw = get_with_retries(
                        session, txt_url, timeout=(10, 90), attempts=2,
                        log=self.stderr.write,
                    ).text
                except requests.RequestException as exc:
                    self.stderr.write(f"[reseau] Livre {item['id']} ignore : {exc}")
                    continue
                text = strip_gutenberg(raw)
                words = len(text.split())
                if words < MIN_WORDS:
                    continue
                name = f"{item['id']}.txt"
                (corpus / name).write_text(text, encoding="utf-8")
                author = item["authors"][0]["name"] if item["authors"] else ""
                Book.objects.create(
                    gutenberg_id=item["id"], title=item["title"][:500], author=author[:300],
                    language=(item["languages"] or ["en"])[0], text_path=name, word_count=words,
                )
                count += 1
                self.stdout.write(f"[{count}/{target}] {item['id']} {item['title'][:60]}")
                time.sleep(0.2)  # politesse envers les serveurs
            url = data.get("next")
        self.stdout.write(self.style.SUCCESS(f"{count} livres dans la base."))
