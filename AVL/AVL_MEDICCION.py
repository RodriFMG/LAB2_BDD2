import os
import struct
import time
import csv

import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from AVL.AVLfile import AVLFile
from BST.Venta import Venta


def cargar_ventasAVL(csv_path):
    ventas = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        lector = csv.DictReader(csvfile)
        for fila in lector:
            venta = Venta(
                int(fila["ID de la venta"]),
                fila["Nombre producto"],
                int(fila["Cantidad vendida"]),
                float(fila["Precio unitario"]),
                fila["Fecha de venta"]
            )
            ventas.append(venta)
    return ventas


def benchmark_avl(filename, ventas):
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, "wb") as f:
        f.write(struct.pack("i", -1))  # raíz = -1

    avl = AVLFile(filename)

    tiempos = {}

    # 1. Inserción
    inicio = time.perf_counter()
    for v in ventas:
        avl.insert(v)
    fin = time.perf_counter()
    tiempos["inserción"] = fin - inicio

    # 2. Búsqueda específica
    ids_buscar = [ventas[0].id, ventas[len(ventas) // 2].id, ventas[-1].id]
    inicio = time.perf_counter()
    for id in ids_buscar:
        avl.search(id)
    fin = time.perf_counter()
    tiempos["búsqueda específica"] = fin - inicio

    # 3. Búsqueda por rango
    inicio = time.perf_counter()
    avl.search_range(ventas[0].id, ventas[-1].id)
    fin = time.perf_counter()
    tiempos["búsqueda por rango"] = fin - inicio

    # 4. Eliminación
    ids_eliminar = [ventas[0].id, ventas[-1].id]
    inicio = time.perf_counter()
    for id in ids_eliminar:
        avl.remove(id)
    fin = time.perf_counter()
    tiempos["eliminación"] = fin - inicio

    # os.remove(filename)  # limpiar

    return tiempos


def graficar_resultados(tiempos):
    operaciones = list(tiempos.keys())
    duraciones = list(tiempos.values())

    plt.figure(figsize=(8, 5))
    plt.bar(operaciones, duraciones, color="skyblue")
    plt.ylabel("Tiempo (segundos)")
    plt.title("Evaluación de Desempeño - AVL persistente")
    plt.grid(axis="y")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    csv_path = "../sales_dataset.csv"
    filename = "avl_perf.dat"
    ventas = cargar_ventasAVL(csv_path)
    tiempos = benchmark_avl(filename, ventas)
    print("\n--- Resultados de Desempeño ---")
    for k, v in tiempos.items():
        print(f"{k}: {v:.6f} segundos")
    graficar_resultados(tiempos)
