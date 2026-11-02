"""Tests du comportement reseau, sans telechargement effectif."""
from unittest import TestCase
from unittest.mock import Mock, patch

import requests

from books.gutenberg_http import get_with_retries


class HttpRetryTests(TestCase):
    @patch("books.gutenberg_http.time.sleep")
    def test_retry_apres_timeout(self, sleep):
        expected = Mock()
        expected.raise_for_status.return_value = None
        session = Mock()
        session.get.side_effect = [requests.ReadTimeout("lent"), expected]
        self.assertIs(get_with_retries(session, "https://example.test", attempts=3), expected)
        self.assertEqual(session.get.call_count, 2)
        sleep.assert_called_once_with(5)

    @patch("books.gutenberg_http.time.sleep")
    def test_echec_definitif_remonte_erreur(self, sleep):
        session = Mock()
        session.get.side_effect = requests.ReadTimeout("hors ligne")
        with self.assertRaises(requests.ReadTimeout):
            get_with_retries(session, "https://example.test", attempts=3)
        self.assertEqual(session.get.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    @patch("books.gutenberg_http.time.sleep")
    def test_pas_de_retry_si_succes(self, sleep):
        expected = Mock()
        expected.raise_for_status.return_value = None
        session = Mock()
        session.get.return_value = expected
        self.assertIs(get_with_retries(session, "https://example.test"), expected)
        sleep.assert_not_called()
