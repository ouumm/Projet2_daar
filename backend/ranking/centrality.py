"""Indices de centralite sur un graphe non oriente (dict sommet -> ensemble de voisins).

- closeness : (n_atteignables - 1) / somme des distances (BFS), normalise par la composante.
- pagerank : iteration de puissance, facteur d'amortissement d = 0.85.
- betweenness : TODO (algorithme de Brandes), a ajouter si on veut comparer pour le rapport.
"""
from collections import deque


def closeness(graph: dict) -> dict:
    res = {}
    for s in graph:
        dist = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            for v in graph[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        total = sum(dist.values())
        res[s] = (len(dist) - 1) / total if total > 0 else 0.0
    return res


def pagerank(graph: dict, d: float = 0.85, iters: int = 100, tol: float = 1e-10) -> dict:
    n = len(graph)
    if n == 0:
        return {}
    pr = {v: 1.0 / n for v in graph}
    for _ in range(iters):
        dangling = sum(pr[v] for v in graph if not graph[v])
        new = {}
        for v in graph:
            incoming = sum(pr[u] / len(graph[u]) for u in graph[v])
            new[v] = (1 - d) / n + d * (incoming + dangling / n)
        delta = sum(abs(new[v] - pr[v]) for v in graph)
        pr = new
        if delta < tol:
            break
    return pr
