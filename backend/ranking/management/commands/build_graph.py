"""Construit le graphe de Jaccard puis calcule closeness et pagerank.

Usage : python manage.py build_graph [--top-terms 1000] [--threshold 0.3]
Chaque livre est represente par l'ensemble de ses `top-terms` mots les plus frequents.
"""
from django.core.management.base import BaseCommand

from books.models import Book
from ranking import centrality, jaccard
from ranking.models import JaccardEdge
from search.models import Posting


class Command(BaseCommand):
    help = "Graphe de Jaccard + centralites (closeness, pagerank)."

    def add_arguments(self, parser):
        parser.add_argument("--top-terms", type=int, default=1000)
        parser.add_argument("--threshold", type=float, default=0.3)

    def handle(self, *args, **opts):
        sets = {}
        for book in Book.objects.all():
            terms = (Posting.objects.filter(book=book).order_by("-count")
                     .values_list("term", flat=True)[:opts["top_terms"]])
            sets[book.id] = set(terms)
        edges = jaccard.build_edges(sets, opts["threshold"])
        JaccardEdge.objects.all().delete()
        JaccardEdge.objects.bulk_create(
            [JaccardEdge(a_id=i, b_id=j, similarity=s) for i, j, s in edges], batch_size=5000)
        graph = {i: set() for i in sets}
        for i, j, _ in edges:
            graph[i].add(j)
            graph[j].add(i)
        pr, cl = centrality.pagerank(graph), centrality.closeness(graph)
        for b in Book.objects.all():
            b.pagerank, b.closeness = pr.get(b.id, 0.0), cl.get(b.id, 0.0)
            b.save(update_fields=["pagerank", "closeness"])
        self.stdout.write(self.style.SUCCESS(f"{len(edges)} aretes, {len(sets)} sommets."))
