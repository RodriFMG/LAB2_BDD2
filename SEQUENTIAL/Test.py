import os
import struct
import time
import csv

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from SEQUENTIAL.sequential_file import (
    insertar_registro,
    buscar_por_id,
    eliminar_por_id,
    buscar_por_rango
)

# Rutas
csv_path = "../sales_dataset.csv"
main_file_path = "../SEQUENTIAL/sequential_file.dat"
aux_file_path = "../SEQUENTIAL/aux_file.dat"

record_size = struct.calcsize("i30sif10sB")


def cargar_ventasSEQUENTIAL(csv_path):
    ventas = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        lector = csv.DictReader(csvfile)
        for fila in lector:
            ventas.append({
                "id": int(fila["ID de la venta"]),
                "nombre": fila["Nombre producto"],
                "cantidad": int(fila["Cantidad vendida"]),
                "precio": float(fila["Precio unitario"]),
                "fecha": fila["Fecha de venta"]
            })
    return ventas


def benchmark_sequential(csv_path, ventas):
    os.makedirs("../SEQUENTIAL", exist_ok=True)
    if os.path.exists(main_file_path):
        os.remove(main_file_path)
    if os.path.exists(aux_file_path):
        os.remove(aux_file_path)

    tiempos = {}

    # 1. Inserción (1000)
    inicio = time.perf_counter()
    with open(main_file_path, "wb") as f:
        for venta in ventas:
            insertar_registro(
                venta["id"], venta["nombre"], venta["cantidad"], venta["precio"], venta["fecha"]
            )
    fin = time.perf_counter()
    tiempos["inserción"] = fin - inicio

    # 2. Búsqueda específica
    ids_buscar = [ventas[0]["id"], ventas[len(ventas)//2]["id"], ventas[-1]["id"]]
    inicio = time.perf_counter()
    for id_venta in ids_buscar:
        buscar_por_id(id_venta)
    fin = time.perf_counter()
    tiempos["búsqueda específica"] = fin - inicio

    # 3. Búsqueda por rango
    inicio = time.perf_counter()
    buscar_por_rango(ventas[0]["id"], ventas[-1]["id"])
    fin = time.perf_counter()
    tiempos["búsqueda por rango"] = fin - inicio

    # 4. Eliminación
    ids_eliminar = [ventas[0]["id"], ventas[-1]["id"]]
    inicio = time.perf_counter()
    for id_venta in ids_eliminar:
        eliminar_por_id(id_venta)
    fin = time.perf_counter()
    tiempos["eliminación"] = fin - inicio

    return tiempos


def graficar_resultados(tiempos):
    operaciones = list(tiempos.keys())
    duraciones = list(tiempos.values())

    plt.figure(figsize=(8, 5))
    plt.bar(operaciones, duraciones, color="lightgreen")
    plt.ylabel("Tiempo (segundos)")
    plt.title("Evaluación de Desempeño - Archivo Secuencial")
    plt.grid(axis="y")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    ventas = cargar_ventasSEQUENTIAL(csv_path)
    tiempos = benchmark_sequential(csv_path, ventas)
    print("\n--- Resultados de Desempeño ---")
    for k, v in tiempos.items():
        print(f"{k}: {v:.6f} segundos")
    graficar_resultados(tiempos)