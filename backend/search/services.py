import re
from collections import defaultdict
from pathlib import Path

from django.conf import settings
from django.db.models import Sum

from books.models import Book
from ranking.services import suggest
from . import kmp
from .models import Posting, Term

_vocab_cache = {"n": -1, "terms": []}


def vocabulary() -> list[str]:
    n = Term.objects.count()
    if n != _vocab_cache["n"]:
        _vocab_cache["terms"] = list(Term.objects.values_list("term", flat=True))
        _vocab_cache["n"] = n
    return _vocab_cache["terms"]


def counts_for_terms(terms: list[str]) -> dict[int, int]:
    rows = (Posting.objects.filter(term__in=terms)
            .values("book_id").annotate(total=Sum("count")))
    return {r["book_id"]: r["total"] for r in rows}


def keyword_counts(q: str, mode: str = "exact") -> dict[int, int]:
    q = q.lower().strip()
    if mode == "contains":
        # KMP applique a chaque mot du vocabulaire
        terms = [t for t in vocabulary() if kmp.contains(t, q)]
    else:
        terms = [q]
    return counts_for_terms(terms)


def regex_index_counts(rx: re.Pattern) -> dict[int, int]:
    terms = [t for t in vocabulary() if rx.search(t)]
    return counts_for_terms(terms)


def regex_content_counts(rx: re.Pattern, max_books: int | None = None) -> dict[int, int]:
    """Parcourt le texte complet de chaque livre (lent, a benchmarker)."""
    res = {}
    for book in Book.objects.all()[:max_books]:
        path = Path(settings.CORPUS_DIR) / book.text_path
        if path.exists():
            n = sum(1 for _ in rx.finditer(path.read_text(encoding="utf-8", errors="ignore")))
            if n:
                res[book.id] = n
    return res


RANK_KEYS = {
    "occurrences": lambda b, c: (-c, -b.pagerank),
    "pagerank": lambda b, c: (-b.pagerank, -c),
    "closeness": lambda b, c: (-b.closeness, -c),
}


def build_response(counts: dict[int, int], rank: str = "occurrences", limit: int = 50) -> dict:
    books = {b.id: b for b in Book.objects.filter(id__in=counts.keys())}
    key = RANK_KEYS.get(rank, RANK_KEYS["occurrences"])
    ordered = sorted(books.values(), key=lambda b: key(b, counts[b.id]))
    results = [
        {"id": b.id, "gutenberg_id": b.gutenberg_id, "title": b.title, "author": b.author,
         "language": b.language, "occurrences": counts[b.id],
         "pagerank": b.pagerank, "closeness": b.closeness, "clicks": b.clicks}
        for b in ordered[:limit]
    ]
    top_ids = [r["id"] for r in results[:3]]
    return {
        "count": len(ordered),
        "rank": rank,
        "results": results,
        "suggestions": suggest(top_ids, exclude=[r["id"] for r in results]),
    }
