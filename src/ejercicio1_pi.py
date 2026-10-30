"""Ejercicio 1: speedup paralelo de estimate_pi (Monte Carlo) con 1, 2, 4 y 8 procesos."""
import time, os
import numpy as np
import multiprocessing as mp
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

N_TOTAL = 40_000_000       # muestras totales (escalamiento fuerte: tamano fijo)
REPETICIONES = 5

def _contar(args):
    n, semilla = args
    rng = np.random.default_rng(semilla)
    dentro, resto = 0, n
    while resto > 0:                      # por bloques para no agotar memoria
        m = min(resto, 2_000_000)
        xy = rng.random((m, 2))
        dentro += int(np.count_nonzero((xy ** 2).sum(1) <= 1.0))
        resto -= m
    return dentro

def estimate_pi(n_muestras, n_procesos, semilla=0):
    partes = [n_muestras // n_procesos] * n_procesos
    partes[0] += n_muestras - sum(partes)
    tareas = [(p, semilla + i) for i, p in enumerate(partes)]
    if n_procesos == 1:
        total = _contar(tareas[0])
    else:
        with mp.Pool(n_procesos) as pool:
            total = sum(pool.map(_contar, tareas))
    return 4.0 * total / n_muestras

def main():
    procesos = [1, 2, 4, 8]
    tiempos = {}
    for p in procesos:
        ts = []
        for r in range(REPETICIONES):
            t0 = time.perf_counter()
            pi_est = estimate_pi(N_TOTAL, p, semilla=100 * r)
            ts.append(time.perf_counter() - t0)
        tiempos[p] = float(np.median(ts))
        print(f"p={p}: t={tiempos[p]:.3f}s  pi~{pi_est:.6f}")
    speedup = [tiempos[1] / tiempos[p] for p in procesos]
    eficiencia = [s / p for s, p in zip(speedup, procesos)]

    with open("results/ej1_speedup.csv", "w") as f:
        f.write("procesos,tiempo_s,speedup,eficiencia\n")
        for p, s, e in zip(procesos, speedup, eficiencia):
            f.write(f"{p},{tiempos[p]:.4f},{s:.3f},{e:.3f}\n")

    plt.figure(figsize=(6, 4.5))
    plt.plot(procesos, procesos, "k--", label="Speedup ideal (lineal)")
    plt.plot(procesos, speedup, "o-", color="tab:blue", label="Speedup medido")
    plt.xlabel("Numero de procesos"); plt.ylabel("Speedup = T1 / Tp")
    plt.title(f"estimate_pi: aceleracion paralela ({os.cpu_count()} nucleo(s) disponibles)")
    plt.xticks(procesos); plt.grid(alpha=.3); plt.legend()
    plt.tight_layout(); plt.savefig("figures/ej1_speedup.png", dpi=150)

if __name__ == "__main__":
    main()
