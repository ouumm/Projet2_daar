from django.db.models import Q

from books.models import Book
from .models import JaccardEdge


def neighbors(book_id: int) -> dict[int, float]:
    res = {}
    for e in JaccardEdge.objects.filter(Q(a_id=book_id) | Q(b_id=book_id)):
        res[e.b_id if e.a_id == book_id else e.a_id] = e.similarity
    return res


def suggest(top_ids: list[int], exclude: list[int] | None = None, limit: int = 6) -> list[dict]:
    """Voisins (graphe de Jaccard) des documents les plus pertinents, tries par clics puis similarite."""
    exclude = set(exclude or [])
    score: dict[int, float] = {}
    for bid in top_ids:
        for nid, sim in neighbors(bid).items():
            if nid not in exclude:
                score[nid] = max(score.get(nid, 0.0), sim)
    books = Book.objects.in_bulk(score.keys())
    ordered = sorted(books.values(), key=lambda b: (-b.clicks, -score[b.id]))[:limit]
    return [{"id": b.id, "title": b.title, "author": b.author,
             "similarity": round(score[b.id], 3), "clicks": b.clicks} for b in ordered]
