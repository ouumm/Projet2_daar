import re

from rest_framework.response import Response
from rest_framework.views import APIView

from . import services


class SearchView(APIView):
    """GET /api/search/?q=mot&mode=exact|contains&rank=occurrences|pagerank|closeness"""

    def get(self, request):
        q = request.query_params.get("q", "").strip()
        if not q:
            return Response({"detail": "parametre q requis"}, status=400)
        counts = services.keyword_counts(q, request.query_params.get("mode", "exact"))
        return Response(services.build_response(counts, request.query_params.get("rank", "occurrences")))


class AdvancedSearchView(APIView):
    """GET /api/search/advanced/?regex=...&scope=index|content&rank=..."""

    def get(self, request):
        pattern = request.query_params.get("regex", "")
        if not pattern or len(pattern) > 100:
            return Response({"detail": "regex requise (100 caracteres max)"}, status=400)
        try:
            rx = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            return Response({"detail": f"regex invalide : {e}"}, status=400)
        # TODO: remplacer `re` par notre propre automate (cours Aho-Ullman) pour le rapport
        if request.query_params.get("scope", "index") == "content":
            counts = services.regex_content_counts(rx)
        else:
            counts = services.regex_index_counts(rx)
        return Response(services.build_response(counts, request.query_params.get("rank", "occurrences")))
