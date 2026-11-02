from django.db.models import F
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
from pathlib import Path

from .models import Book
from .serializers import BookSerializer


class BookList(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookDetail(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookClick(APIView):
    """Enregistre un clic (alimente la suggestion par popularite)."""

    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        Book.objects.filter(pk=pk).update(clicks=F("clicks") + 1)
        book.refresh_from_db()
        return Response({"id": book.id, "clicks": book.clicks})


class BookText(APIView):
    """Extrait du texte (premiers caracteres) pour l'affichage."""

    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        path = Path(settings.CORPUS_DIR) / book.text_path
        n = int(request.query_params.get("n", 3000))
        text = path.read_text(encoding="utf-8", errors="ignore")[:n] if path.exists() else ""
        return Response({"id": book.id, "excerpt": text})
