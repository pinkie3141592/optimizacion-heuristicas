"""Utilidades compartidas: instancias TSP, 2-opt, vecino mas cercano, MST, Held-Karp."""
import numpy as np
import math

def instancia_aleatoria(n, rng):
    """n ciudades uniformes en el cuadrado unitario."""
    return rng.random((n, 2))

def matriz_distancias(coords):
    d = coords[:, None, :] - coords[None, :, :]
    return np.sqrt((d ** 2).sum(-1))

def costo_tour(D, tour):
    return float(sum(D[tour[i], tour[(i + 1) % len(tour)]] for i in range(len(tour))))

def vecino_mas_cercano(D, inicio):
    n = len(D)
    visitado = [False] * n
    tour = [inicio]; visitado[inicio] = True
    while len(tour) < n:
        u = tour[-1]
        v = min((j for j in range(n) if not visitado[j]), key=lambda j: D[u, j])
        tour.append(v); visitado[v] = True
    return tour

def dos_opt(D, tour):
    """2-opt con primera mejora hasta optimo local.
    Devuelve (tour, numero_de_mejoras_aplicadas)."""
    tour = list(tour); n = len(tour); mejoras = 0
    mejorado = True
    while mejorado:
        mejorado = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue
                a, b = tour[i], tour[i + 1]
                c, d = tour[j], tour[(j + 1) % n]
                delta = D[a, c] + D[b, d] - D[a, b] - D[c, d]
                if delta < -1e-12:
                    tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
                    mejoras += 1; mejorado = True
    return tour, mejoras

def mst_prim(D):
    """Devuelve lista de adyacencia del MST (Prim) y su costo."""
    n = len(D)
    en_mst = [False] * n; dist = [math.inf] * n; padre = [-1] * n
    dist[0] = 0; adj = [[] for _ in range(n)]; costo = 0.0
    for _ in range(n):
        u = min((i for i in range(n) if not en_mst[i]), key=lambda i: dist[i])
        en_mst[u] = True; costo += dist[u]
        if padre[u] >= 0:
            adj[u].append(padre[u]); adj[padre[u]].append(u)
        for v in range(n):
            if not en_mst[v] and D[u, v] < dist[v]:
                dist[v] = D[u, v]; padre[v] = u
    return adj, costo

def tour_aproximado_mst(D):
    """2-aproximacion: recorrido en preorden del MST (atajos por desigualdad triangular)."""
    adj, costo_mst = mst_prim(D)
    tour, visto = [], set()
    def dfs(u):
        visto.add(u); tour.append(u)
        for v in adj[u]:
            if v not in visto:
                dfs(v)
    dfs(0)
    return tour, costo_mst

def optimo_held_karp(D):
    """Optimo exacto (programacion dinamica, O(n^2 2^n)); valido para n<=~12."""
    n = len(D); INF = float("inf")
    dp = {(1, 0): 0.0}
    for mask in range(1, 1 << n):
        if not mask & 1:
            continue
        for last in range(n):
            if (mask, last) not in dp:
                continue
            c = dp[(mask, last)]
            for nxt in range(n):
                if mask & (1 << nxt):
                    continue
                key = (mask | (1 << nxt), nxt)
                v = c + D[last, nxt]
                if v < dp.get(key, INF):
                    dp[key] = v
    full = (1 << n) - 1
    return min(dp[(full, l)] + D[l, 0] for l in range(1, n))
