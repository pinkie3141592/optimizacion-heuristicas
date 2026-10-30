"""Ejecuta todos los experimentos y regenera figuras/ y results/ (desde la raiz del repo)."""
import subprocess, sys
for s in ["ejercicio1_pi", "ejercicio2_knapsack", "ejercicio3_2opt", "ejercicio4_sa", "ejercicio5_mst"]:
    print(f"\n>>> {s}"); subprocess.run([sys.executable, f"src/{s}.py"], check=True)
