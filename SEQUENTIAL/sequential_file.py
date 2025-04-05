import os
import pandas as pd
from SEQUENTIAL.venta_secuencial import VentaSecuencial
import struct
import math

def calcular_k(tamano_archivo_bytes, record_size):
    n = tamano_archivo_bytes // record_size
    k = max(1, round(math.log2(n)))
    return k


csv_path = "./sales_dataset.csv"
main_file_path = "./SEQUENTIAL/sequential_file.dat"
aux_file_path = "./SEQUENTIAL/aux_file.dat"
record_size = struct.calcsize("i30sif10sB")

# Crear archivo secuencial ordenado desde CSV
def crear_archivo_secuencial(csv_path):
    df = pd.read_csv(csv_path)
    df = df.sort_values(by="ID de la venta")
    with open(main_file_path, "wb") as f:
        for _, row in df.iterrows():
            venta = VentaSecuencial(int(row["ID de la venta"]),
                                    row["Nombre producto"],
                                    int(row["Cantidad vendida"]),
                                    float(row["Precio unitario"]),
                                    row["Fecha de venta"])
            f.write(venta.to_byte())
    open(aux_file_path, "wb").close()

# Insertar registro en auxiliar
def insertar_registro(id_venta, nombre_producto, cantidad, precio, fecha):
    venta = VentaSecuencial(id_venta, nombre_producto, cantidad, precio, fecha)
    with open(aux_file_path, "ab") as f:
        f.write(venta.to_byte())

    tamano_archivo = os.path.getsize(main_file_path)
    n = tamano_archivo // record_size
    k_dinamico = max(1, round(math.log2(n))) if n > 0 else 1

    # Verificar si auxiliar excede el nuevo k
    if os.path.getsize(aux_file_path) // record_size >= k_dinamico:
        reconstruir_archivo()

# Reconstrucción del archivo principal
def reconstruir_archivo():
    registros = []

    for path in [main_file_path, aux_file_path]:
        with open(path, "rb") as f:
            while data := f.read(record_size):
                venta = VentaSecuencial.to_data(data)
                if not venta.eliminado:
                    registros.append(venta)

    registros.sort(key=lambda x: x.id)

    with open(main_file_path, "wb") as f:
        for venta in registros:
            f.write(venta.to_byte())

    open(aux_file_path, "wb").close()

# Buscar por ID
def buscar_por_id(id_venta):
    for path in [main_file_path, aux_file_path]:
        with open(path, "rb") as f:
            while data := f.read(record_size):
                venta = VentaSecuencial.to_data(data)
                if not venta.eliminado and venta.id == id_venta:
                    return venta
    return None

# Eliminar un registro lógicamente
def eliminar_por_id(id_venta):
    for path in [main_file_path, aux_file_path]:
        with open(path, "r+b") as f:
            pos = 0
            while data := f.read(record_size):
                venta = VentaSecuencial.to_data(data)
                if not venta.eliminado and venta.id == id_venta:
                    venta.eliminado = True
                    f.seek(pos)
                    f.write(venta.to_byte())
                    return True
                pos += record_size
    return False

# Buscar por rango de ID
def buscar_por_rango(id_inicio, id_fin):
    resultados = []
    for path in [main_file_path, aux_file_path]:
        with open(path, "rb") as f:
            while data := f.read(record_size):
                venta = VentaSecuencial.to_data(data)
                if not venta.eliminado and id_inicio <= venta.id <= id_fin:
                    resultados.append(venta)
    return sorted(resultados, key=lambda x: x.id)