"""Ejercicio 3: 2-opt desde solucion inicial aleatoria vs. Vecino Mas Cercano (inicio aleatorio)."""
import numpy as np, random
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import *

N_CIUDADES, N_INSTANCIAS = 50, 100

def main():
    rng = np.random.default_rng(42); rnd = random.Random(42)
    res = {"aleatoria": {"mejoras": [], "inicial": [], "final": []},
           "NN":        {"mejoras": [], "inicial": [], "final": []}}
    for _ in range(N_INSTANCIAS):
        D = matriz_distancias(instancia_aleatoria(N_CIUDADES, rng))
        t_rand = list(range(N_CIUDADES)); rnd.shuffle(t_rand)
        t_nn = vecino_mas_cercano(D, rnd.randrange(N_CIUDADES))
        for k, t0 in [("aleatoria", t_rand), ("NN", t_nn)]:
            t, m = dos_opt(D, t0)
            res[k]["mejoras"].append(m)
            res[k]["inicial"].append(costo_tour(D, t0)); res[k]["final"].append(costo_tour(D, t))

    with open("results/ej3_resumen.csv", "w") as f:
        f.write("inicio,mejoras_media,mejoras_mediana,costo_inicial_medio,costo_optimo_local_medio,costo_optimo_local_std\n")
        for k, r in res.items():
            f.write(f"{k},{np.mean(r['mejoras']):.2f},{np.median(r['mejoras']):.1f},"
                    f"{np.mean(r['inicial']):.3f},{np.mean(r['final']):.3f},{np.std(r['final']):.3f}\n")
            print(k, "mejoras media=%.1f mediana=%.1f | costo inicial=%.2f | optimo local=%.3f +- %.3f" %
                  (np.mean(r['mejoras']), np.median(r['mejoras']), np.mean(r['inicial']),
                   np.mean(r['final']), np.std(r['final'])))
    from scipy import stats  # prueba pareada (opcional)
    for m in ["mejoras", "final"]:
        t, p = stats.wilcoxon(res["aleatoria"][m], res["NN"][m])
        print(f"Wilcoxon pareado ({m}): p={p:.2e}")

    etiquetas = ["Inicio aleatorio", "Vecino mas cercano"]
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.2))
    ax[0].boxplot([res["aleatoria"]["mejoras"], res["NN"]["mejoras"]], tick_labels=etiquetas)
    ax[0].set_ylabel("Mejoras 2-opt hasta optimo local"); ax[0].set_title("Numero de mejoras")
    ax[1].boxplot([res["aleatoria"]["final"], res["NN"]["final"]], tick_labels=etiquetas)
    ax[1].set_ylabel("Costo del optimo local"); ax[1].set_title("Calidad del optimo local alcanzado")
    for a in ax: a.grid(alpha=.3)
    fig.suptitle(f"2-opt: {N_INSTANCIAS} instancias de {N_CIUDADES} ciudades"); plt.tight_layout()
    plt.savefig("figures/ej3_boxplots.png", dpi=150)

if __name__ == "__main__":
    main()
