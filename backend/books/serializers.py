from rest_framework import serializers

from .models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "gutenberg_id", "title", "author", "language",
                  "word_count", "clicks", "pagerank", "closeness"]
