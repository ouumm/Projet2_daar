"""Algorithme de Knuth-Morris-Pratt (recherche d'un facteur dans un mot). Complexite O(n + m)."""


def failure_table(pattern: str) -> list[int]:
    """table[i] = longueur du plus long bord propre de pattern[:i+1]."""
    table = [0] * len(pattern)
    k = 0
    for i in range(1, len(pattern)):
        while k > 0 and pattern[i] != pattern[k]:
            k = table[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        table[i] = k
    return table


def find_all(text: str, pattern: str) -> list[int]:
    """Positions de toutes les occurrences (eventuellement chevauchantes) de pattern dans text."""
    if not pattern:
        return []
    table = failure_table(pattern)
    res, k = [], 0
    for i, c in enumerate(text):
        while k > 0 and c != pattern[k]:
            k = table[k - 1]
        if c == pattern[k]:
            k += 1
        if k == len(pattern):
            res.append(i - k + 1)
            k = table[k - 1]
    return res


def contains(text: str, pattern: str) -> bool:
    return bool(pattern) and bool(find_all(text, pattern))
