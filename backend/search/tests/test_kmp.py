from django.test import SimpleTestCase

from search import kmp


class KmpTests(SimpleTestCase):
    def test_failure_table(self):
        self.assertEqual(kmp.failure_table("abacabab"), [0, 0, 1, 0, 1, 2, 3, 2])

    def test_find_all_overlapping(self):
        self.assertEqual(kmp.find_all("aaaa", "aa"), [0, 1, 2])

    def test_find_all_basic(self):
        self.assertEqual(kmp.find_all("abracadabra", "abra"), [0, 7])

    def test_not_found_and_empty(self):
        self.assertEqual(kmp.find_all("hello", "xyz"), [])
        self.assertEqual(kmp.find_all("hello", ""), [])

    def test_matches_python_find(self):
        text = "the quick brown fox jumps over the lazy dog " * 20
        for p in ["the", "fox j", "dog t", "zzz"]:
            expected = [i for i in range(len(text)) if text.startswith(p, i)]
            self.assertEqual(kmp.find_all(text, p), expected)
