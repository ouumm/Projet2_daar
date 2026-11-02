from django.test import SimpleTestCase

from ranking import centrality, jaccard


class JaccardTests(SimpleTestCase):
    def test_similarity(self):
        self.assertAlmostEqual(jaccard.similarity({"a", "b", "c"}, {"b", "c", "d"}), 0.5)
        self.assertAlmostEqual(jaccard.distance({"a"}, {"a"}), 0.0)
        self.assertAlmostEqual(jaccard.distance({"a"}, {"b"}), 1.0)

    def test_build_edges_threshold(self):
        sets = {1: {"a", "b"}, 2: {"a", "b", "c"}, 3: {"x"}}
        edges = jaccard.build_edges(sets, 0.5)
        self.assertEqual([(i, j) for i, j, _ in edges], [(1, 2)])


class CentralityTests(SimpleTestCase):
    star = {0: {1, 2, 3}, 1: {0}, 2: {0}, 3: {0}}
    path = {1: {2}, 2: {1, 3}, 3: {2}}

    def test_closeness_star(self):
        c = centrality.closeness(self.star)
        self.assertAlmostEqual(c[0], 1.0)          # 3 / (1+1+1)
        self.assertAlmostEqual(c[1], 3 / 5)        # 3 / (1+2+2)

    def test_closeness_path(self):
        c = centrality.closeness(self.path)
        self.assertGreater(c[2], c[1])

    def test_pagerank_sums_to_one_and_center_wins(self):
        pr = centrality.pagerank(self.star)
        self.assertAlmostEqual(sum(pr.values()), 1.0, places=6)
        self.assertGreater(pr[0], pr[1])
        self.assertAlmostEqual(pr[1], pr[2])

    def test_isolated_vertex(self):
        pr = centrality.pagerank({1: set(), 2: set()})
        self.assertAlmostEqual(pr[1], 0.5)
        self.assertEqual(centrality.closeness({1: set()})[1], 0.0)
