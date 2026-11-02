from django.db import models


class Book(models.Model):
    gutenberg_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=300, blank=True)
    language = models.CharField(max_length=10, default="en")
    text_path = models.CharField(max_length=500)  # fichier .txt dans CORPUS_DIR
    word_count = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)  # pour la suggestion "les plus cliques"
    # scores de centralite precalcules (app ranking)
    pagerank = models.FloatField(default=0.0)
    closeness = models.FloatField(default=0.0)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.gutenberg_id} - {self.title}"
