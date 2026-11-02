from django.db import models

from books.models import Book


class JaccardEdge(models.Model):
    """Arete du graphe de Jaccard (graphe non oriente, a < b)."""
    a = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="edges_a")
    b = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="edges_b")
    similarity = models.FloatField()  # 1 - distance de Jaccard

    class Meta:
        unique_together = ("a", "b")
