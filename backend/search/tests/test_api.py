import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase, override_settings

from books.models import Book
from ranking.models import JaccardEdge

TEXTS = {
    1: "whale whale whale ocean ship captain sea whale ocean ship",
    2: "ocean ocean ship sailor sea wave ocean ship",
    3: "garden flower garden rose flower garden rose",
}


class ApiTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.override = override_settings(CORPUS_DIR=Path(cls.tmp.name))
        cls.override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.override.disable()
        cls.tmp.cleanup()
        super().tearDownClass()

    def setUp(self):
        for gid, text in TEXTS.items():
            (Path(self.tmp.name) / f"{gid}.txt").write_text(text)
            Book.objects.create(gutenberg_id=gid, title=f"Book {gid}", text_path=f"{gid}.txt",
                                word_count=len(text.split()))
        call_command("build_index", "--min-count", "1", verbosity=0)
        call_command("build_graph", "--top-terms", "50", "--threshold", "0.2", verbosity=0)

    def test_books_endpoints(self):
        self.assertEqual(self.client.get("/api/books/").json()["count"], 3)
        self.assertEqual(self.client.get("/api/book/1/").status_code, 200)
        self.assertEqual(self.client.get("/api/book/999/").status_code, 404)

    def test_search_exact_and_ranking_by_occurrences(self):
        r = self.client.get("/api/search/?q=ocean").json()
        self.assertEqual([x["gutenberg_id"] for x in r["results"]], [2, 1])
        self.assertEqual(r["results"][0]["occurrences"], 3)

    def test_search_requires_q(self):
        self.assertEqual(self.client.get("/api/search/").status_code, 400)

    def test_search_contains_uses_kmp(self):
        r = self.client.get("/api/search/?q=ocea&mode=contains").json()
        self.assertEqual(r["count"], 2)

    def test_advanced_regex_index_and_content(self):
        r = self.client.get("/api/search/advanced/?regex=^gard.*").json()
        self.assertEqual([x["gutenberg_id"] for x in r["results"]], [3])
        r = self.client.get("/api/search/advanced/?regex=sh[i]p&scope=content").json()
        self.assertEqual(r["count"], 2)

    def test_advanced_invalid_regex(self):
        self.assertEqual(self.client.get("/api/search/advanced/?regex=(").status_code, 400)

    def test_graph_and_suggestions(self):
        self.assertTrue(JaccardEdge.objects.exists())
        r = self.client.get("/api/search/?q=whale").json()
        self.assertEqual([x["gutenberg_id"] for x in r["results"]], [1])
        self.assertIn(2, [Book.objects.get(id=s["id"]).gutenberg_id for s in r["suggestions"]])

    def test_click_increments(self):
        r = self.client.post("/api/book/1/click/").json()
        self.assertEqual(r["clicks"], 1)
