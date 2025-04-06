from BST.BST_MEDICCION import cargar_ventasBST, benchmark_bst
from AVL.AVL_MEDICCION import cargar_ventasAVL, benchmark_avl
from SEQUENTIAL.Test import cargar_ventasSEQUENTIAL, benchmark_sequential
import numpy as np
import os

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

def graficar_resultados(tiemposAVL, tiemposBST, tiemposSEQUENTIAL):
    operaciones = list(tiemposAVL.keys())
    duracionesAVL = list(tiemposAVL.values())
    duracionesBST = list(tiemposBST.values())
    duracionesSEQUENTIAL = list(tiemposSEQUENTIAL.values())

    # Crear el directorio "Graficas" si no existe
    if not os.path.exists("Graficas"):
        os.makedirs("Graficas")

    for i, operacion in enumerate(operaciones):
        fig, ax = plt.subplots(figsize=(8, 5))

        # Nombres y valores
        estructuras = ["AVL", "BST", "Secuencial"]
        valores = [duracionesAVL[i], duracionesBST[i], duracionesSEQUENTIAL[i]]
        colores = ["red", "blue", "green"]

        # Posiciones en el eje x
        x = np.arange(len(estructuras))

        # Dibujar solo una barra por estructura
        ax.bar(x, valores, color=colores)

        # Etiquetas y formato
        ax.set_ylabel("Tiempo (segundos)")
        ax.set_title(f"Desempeño en {operacion}")
        ax.set_xticks(x)
        ax.set_xticklabels(estructuras)
        ax.grid(axis="y")

        # Mostrar valor encima de cada barra
        for xi, yi in zip(x, valores):
            ax.text(xi, yi + 0.002, f"{yi:.4f}", ha="center", va="bottom")

        # Guardar imagen
        fig.tight_layout()
        fig.savefig(f"Graficas/grafico_{operacion}.png")
        plt.close(fig)

if __name__ == "__main__":

    csv_path = "sales_dataset.csv"
    filename = "./AVL/avl_perf.dat"
    ventas = cargar_ventasAVL(csv_path)
    tiemposAVL = benchmark_avl(filename, ventas)

    filename = "./BST/bst_peft.dat"
    ventas = cargar_ventasBST(csv_path)
    tiemposBST = benchmark_bst(filename, ventas)


    ventas = cargar_ventasSEQUENTIAL(csv_path)
    tiemposSEQUENTIAL = benchmark_sequential(csv_path, ventas)

    graficar_resultados(tiemposAVL, tiemposBST, tiemposSEQUENTIAL)
