"""Distance de Jaccard entre deux ensembles de mots : d(A,B) = 1 - |A inter B| / |A union B|."""


def similarity(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def distance(a: set, b: set) -> float:
    return 1.0 - similarity(a, b)


def build_edges(sets: dict[int, set], threshold: float) -> list[tuple[int, int, float]]:
    """Retourne les aretes (i, j, similarite) avec similarite >= threshold, i < j. O(n^2)."""
    ids = sorted(sets)
    edges = []
    for x, i in enumerate(ids):
        for j in ids[x + 1:]:
            s = similarity(sets[i], sets[j])
            if s >= threshold:
                edges.append((i, j, s))
    return edges
