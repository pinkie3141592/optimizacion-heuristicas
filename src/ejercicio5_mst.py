"""Ejercicio 5: razon de aproximacion de la 2-aproximacion por MST (100 instancias, 9 ciudades)."""
import random
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import *
from ejercicio4_sa import recocido

def main():
    rng = np.random.default_rng(2026); rnd = random.Random(2026)
    cols = ["MST puro", "MST + 2-opt", "2-opt (aleatorio)", "2-opt (NN)", "Recocido (exp.)"]
    costos = {c: [] for c in cols}; opt = []; cota_mst = []
    for _ in range(100):
        D = matriz_distancias(instancia_aleatoria(9, rng))
        opt.append(optimo_held_karp(D))
        t_mst, c_mst = tour_aproximado_mst(D); cota_mst.append(c_mst)
        costos["MST puro"].append(costo_tour(D, t_mst))
        costos["MST + 2-opt"].append(costo_tour(D, dos_opt(D, t_mst)[0]))
        t = list(range(9)); rnd.shuffle(t)
        costos["2-opt (aleatorio)"].append(costo_tour(D, dos_opt(D, t)[0]))
        costos["2-opt (NN)"].append(costo_tour(D, dos_opt(D, vecino_mas_cercano(D, rnd.randrange(9)))[0]))
        costos["Recocido (exp.)"].append(recocido(D, "exponencial", 5000, rnd)[0])
    opt = np.array(opt)
    razones = {c: np.array(v) / opt for c, v in costos.items()}

    print(f"{'metodo':20s} {'razon media':>11s} {'mediana':>8s} {'max':>7s} {'% optimo':>9s}")
    with open("results/ej5_razones.csv", "w") as f:
        f.write("metodo,razon_media,razon_mediana,razon_max,razon_min,pct_optimo\n")
        for c, r in razones.items():
            po = 100 * np.mean(r < 1 + 1e-9)
            print(f"{c:20s} {r.mean():11.4f} {np.median(r):8.4f} {r.max():7.4f} {po:8.1f}%")
            f.write(f"{c},{r.mean():.4f},{np.median(r):.4f},{r.max():.4f},{r.min():.4f},{po:.1f}\n")
    print("MST: costo_arbol/optimo medio = %.3f (cota inferior valida: <=1)" % np.mean(np.array(cota_mst) / opt))

    r = razones["MST puro"]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    ax[0].hist(r, bins=20, color="tab:blue", edgecolor="k", alpha=.8)
    ax[0].axvline(2, color="r", ls="--", label="limite teorico = 2")
    ax[0].axvline(r.mean(), color="k", ls=":", label=f"media = {r.mean():.3f}")
    ax[0].set_xlim(1, 2.1); ax[0].set_xlabel("Razon C_obtenido / C_optimo"); ax[0].set_ylabel("Frecuencia")
    ax[0].set_title("Razon de aproximacion (MST puro, 100 instancias)"); ax[0].legend()
    ax[1].scatter(opt, r, s=18, alpha=.7); ax[1].axhline(2, color="r", ls="--", label="limite = 2")
    ax[1].axhline(1, color="g", ls=":", label="optimo"); ax[1].set_ylim(0.95, 2.1)
    ax[1].set_xlabel("Costo optimo (Held-Karp)"); ax[1].set_ylabel("Razon"); ax[1].legend(); ax[1].grid(alpha=.3)
    plt.tight_layout(); plt.savefig("figures/ej5_razon_aproximacion.png", dpi=150); plt.close()

    fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
    ax[0].boxplot([costos[c] for c in cols], tick_labels=cols); ax[0].set_ylabel("Costo del tour")
    ax[0].set_title("Costo obtenido"); ax[0].axhline(np.median(opt), color="g", ls=":", label="mediana optimo"); ax[0].legend()
    ax[1].boxplot([razones[c] for c in cols], tick_labels=cols); ax[1].axhline(1, color="g", ls=":")
    ax[1].set_ylabel("Razon C / C_optimo"); ax[1].set_title("Razon respecto al optimo")
    for a in ax: a.tick_params(axis="x", rotation=20); a.grid(alpha=.3)
    plt.tight_layout(); plt.savefig("figures/ej5_comparacion_metodos.png", dpi=150)

if __name__ == "__main__":
    main()
