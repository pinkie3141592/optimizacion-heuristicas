"""Ejercicio 2: mochila voraz por valor/peso vs. por menor peso."""
import random
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def voraz(items, capacidad, clave):
    """items: lista de (nombre, peso, valor). Recorre en el orden dado por `clave`."""
    sel, peso = [], 0
    for nombre, w, v in sorted(items, key=clave):
        if peso + w <= capacidad:
            sel.append((nombre, w, v)); peso += w
    return sel, peso, sum(v for _, _, v in sel)

por_razon = lambda it: -(it[2] / it[1])      # mayor valor/peso primero
por_peso  = lambda it: it[1]                 # menor peso primero (modificacion)

def optimo_dp(items, capacidad):
    dp = [0] * (capacidad + 1)
    for _, w, v in items:
        for c in range(capacidad, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacidad]

def reporte(items, cap, titulo):
    out = {}
    for nombre, clave in [("valor/peso", por_razon), ("menor peso", por_peso)]:
        out[nombre] = voraz(items, cap, clave)
    opt = optimo_dp(items, cap)
    print(f"\n== {titulo} (capacidad={cap}, optimo={opt}) ==")
    for m, (sel, w, v) in out.items():
        print(f"{m:11s} -> objetos={[s[0] for s in sel]} peso={w} valor={v}")
    return out, opt

def grafica(res, opt, cap, titulo, archivo):
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.8))
    metodos = list(res.keys()); col = ["tab:blue", "tab:orange"]
    ax[0].bar(metodos, [len(res[m][0]) for m in metodos], color=col)
    ax[0].set_title("Objetos seleccionados")
    ax[1].bar(metodos, [res[m][1] for m in metodos], color=col)
    ax[1].axhline(cap, color="k", ls="--", label="capacidad"); ax[1].legend()
    ax[1].set_title("Capacidad usada")
    ax[2].bar(metodos, [res[m][2] for m in metodos], color=col)
    ax[2].axhline(opt, color="g", ls="--", label="optimo (DP)"); ax[2].legend()
    ax[2].set_title("Valor total")
    for a in ax:
        for p in a.patches:
            a.annotate(f"{p.get_height():g}", (p.get_x() + p.get_width() / 2, p.get_height()),
                       ha="center", va="bottom", fontsize=9)
    fig.suptitle(titulo); plt.tight_layout(); plt.savefig(archivo, dpi=150); plt.close()

def guardar_tabla(res, archivo):
    with open(archivo, "w") as f:
        f.write("metodo,objetos,capacidad_usada,valor_total\n")
        for m, (s, w, v) in res.items():
            f.write(f"{m},{' '.join(x[0] for x in s)},{w},{v}\n")

def main():
    rnd = random.Random(7)
    items = [(f"o{i+1}", rnd.randint(2, 20), rnd.randint(5, 60)) for i in range(12)]
    cap = 45
    print("Instancia aleatoria:", items)
    res, opt = reporte(items, cap, "Instancia aleatoria")
    grafica(res, opt, cap, "Instancia aleatoria (12 objetos)", "figures/ej2_instancia_aleatoria.png")
    guardar_tabla(res, "results/ej2_tabla_aleatoria.csv")

    # Contraejemplo disenado: menor peso es MUCHO peor que valor/peso
    contra = [("A", 2, 1), ("B", 3, 1), ("C", 4, 1), ("D", 8, 100)]
    capc = 10
    res, opt = reporte(contra, capc, "Contraejemplo")
    grafica(res, opt, capc, "Contraejemplo: menor peso vs valor/peso", "figures/ej2_contraejemplo.png")
    guardar_tabla(res, "results/ej2_tabla_contraejemplo.csv")

    # Estadistica extra: 2000 instancias aleatorias
    rnd = random.Random(1); peor = igual = mejor = 0
    for _ in range(2000):
        its = [(f"o{i}", rnd.randint(1, 20), rnd.randint(1, 60)) for i in range(10)]
        c = rnd.randint(20, 60)
        vr = voraz(its, c, por_razon)[2]; vp = voraz(its, c, por_peso)[2]
        peor += vp < vr; igual += vp == vr; mejor += vp > vr
    print(f"\n2000 instancias: menor-peso peor={peor}, igual={igual}, mejor={mejor}")

if __name__ == "__main__":
    main()
