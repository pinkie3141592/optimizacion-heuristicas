"""Ejercicio 4: Recocido Simulado (movimiento 2-opt) con distintos esquemas de enfriamiento."""
import math, random, time
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import *

T0, TF = 1.0, 1e-3

def temperatura(esquema, k, N):
    """Todos los esquemas van de T0 a TF en N iteraciones (comparacion justa)."""
    if esquema == "lineal":
        return T0 - (T0 - TF) * k / N
    if esquema == "exponencial":
        return T0 * (TF / T0) ** (k / N)
    if esquema == "logaritmico":
        a = (T0 / TF - 1) / math.log(1 + N)
        return T0 / (1 + a * math.log(1 + k))
    raise ValueError(esquema)

def recocido(D, esquema, N, rnd, traza=False):
    """Devuelve (mejor_costo, mejor_tour, traza_costo_actual, traza_mejor)."""
    n = len(D)
    tour = list(range(n)); rnd.shuffle(tour)          # solucion inicial aleatoria
    costo = costo_tour(D, tour); mejor, mejor_tour = costo, tour[:]
    tr_act, tr_mej = [], []
    for k in range(N):
        T = temperatura(esquema, k, N)
        if traza and k % 50 == 0:
            tr_act.append(costo); tr_mej.append(mejor)
        i, j = sorted(rnd.sample(range(n), 2))
        if i == 0 and j == n - 1:
            continue
        a, b, c, d = tour[i - 1], tour[i], tour[j], tour[(j + 1) % n]   # mov. 2-opt: invertir [i..j]
        delta = D[a, c] + D[b, d] - D[a, b] - D[c, d]
        if delta < 0 or rnd.random() < math.exp(-delta / T):
            tour[i:j + 1] = reversed(tour[i:j + 1]); costo += delta
            if costo < mejor - 1e-12:
                mejor, mejor_tour = costo, tour[:]
    return mejor, mejor_tour, tr_act, tr_mej

ESQUEMAS = ["lineal", "exponencial", "logaritmico"]

def main():
    rng = np.random.default_rng(3)
    D = matriz_distancias(instancia_aleatoria(50, rng))
    N_CONV, REP = 60_000, 10
    colores = {"lineal": "tab:blue", "exponencial": "tab:red", "logaritmico": "tab:green"}

    # (1) Curvas de convergencia (media de REP corridas)
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
    finales = {}
    for e in ESQUEMAS:
        act, mej, fin = [], [], []
        for r in range(REP):
            m, _, a, b = recocido(D, e, N_CONV, random.Random(r), traza=True)
            act.append(a); mej.append(b); fin.append(m)
        act, mej = np.mean(act, 0), np.mean(mej, 0)
        it = np.arange(len(act)) * 50
        ax[0].plot(it, act, color=colores[e], label=e)
        ax[1].plot(it, mej, color=colores[e], label=e)
        ax[2].plot([temperatura(e, k, N_CONV) for k in it], act, color=colores[e], label=e)
        finales[e] = fin
    ax[0].set_title("Costo actual vs iteraciones"); ax[1].set_title("Mejor costo vs iteraciones")
    ax[2].set_title("Costo actual vs temperatura"); ax[2].set_xscale("log"); ax[2].invert_xaxis()
    ax[0].set_xlabel("Iteracion"); ax[1].set_xlabel("Iteracion"); ax[2].set_xlabel("Temperatura (escala log)")
    for a in ax: a.set_ylabel("Costo del tour"); a.grid(alpha=.3); a.legend()
    ax[1].set_ylim(top=ax[1].get_ylim()[0] + 4)
    plt.tight_layout(); plt.savefig("figures/ej4_convergencia.png", dpi=150); plt.close()

    # (2) Tiempo vs calidad variando presupuesto de iteraciones
    presupuestos = [5_000, 20_000, 80_000, 200_000]
    stats = {e: [] for e in ESQUEMAS}
    filas = []
    for e in ESQUEMAS:
        for N in presupuestos:
            ts, cs = [], []
            for r in range(REP):
                t0 = time.perf_counter()
                m, *_ = recocido(D, e, N, random.Random(1000 + r))
                ts.append(time.perf_counter() - t0); cs.append(m)
            stats[e].append((np.mean(ts), np.mean(cs), np.std(cs)))
            filas.append((e, N, np.mean(ts), np.mean(cs), np.std(cs), np.min(cs)))
            print(f"{e:12s} N={N:7d} t={np.mean(ts):6.2f}s costo={np.mean(cs):.3f} +- {np.std(cs):.3f} (min {np.min(cs):.3f})")
    with open("results/ej4_tiempo_calidad.csv", "w") as f:
        f.write("esquema,iteraciones,tiempo_medio_s,costo_medio,costo_std,costo_min\n")
        for r in filas: f.write("%s,%d,%.3f,%.4f,%.4f,%.4f\n" % r)

    plt.figure(figsize=(6.5, 4.5))
    for e in ESQUEMAS:
        t = [s[0] for s in stats[e]]; c = [s[1] for s in stats[e]]; sd = [s[2] for s in stats[e]]
        plt.errorbar(t, c, yerr=sd, fmt="o-", capsize=3, color=colores[e], label=e)
    plt.xscale("log"); plt.xlabel("Tiempo de ejecucion (s, escala log)"); plt.ylabel("Costo final medio (+- desv. est.)")
    plt.title("SA: tiempo vs calidad (4 presupuestos de iteraciones)"); plt.grid(alpha=.3); plt.legend()
    plt.tight_layout(); plt.savefig("figures/ej4_tiempo_vs_calidad.png", dpi=150)

if __name__ == "__main__":
    main()
