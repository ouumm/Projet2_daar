from django.db import models

from books.models import Book


class Term(models.Model):
    """Vocabulaire de l'index (un mot par ligne)."""
    term = models.CharField(max_length=100, unique=True)


class Posting(models.Model):
    """Index inverse : (mot, livre, nombre d'occurrences)."""
    term = models.CharField(max_length=100, db_index=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="postings")
    count = models.IntegerField()

    class Meta:
        unique_together = ("term", "book")
