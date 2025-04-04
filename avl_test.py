import os
import struct
import csv
from AVL.AVLfile import AVLFile
from BST.Venta import Venta

RECORDS_TO_PRINT = 20  # ajusta según la cantidad de registros

def cargar_desde_csv(avl: AVLFile, ruta_csv: str):
    with open(ruta_csv, newline='', encoding='utf-8') as csvfile:
        lector = csv.DictReader(csvfile)
        for fila in lector:
            try:
                venta = Venta(
                    int(fila["ID de la venta"]),
                    fila["Nombre producto"],
                    int(fila["Cantidad vendida"]),
                    float(fila["Precio unitario"]),
                    fila["Fecha de venta"]
                )
                avl.insert(venta)
                print(f"Insertado: {venta}")
            except Exception as e:
                print(f"Error al insertar venta con ID {fila['ID de la venta']}: {e}")

def test_avl():
    filename = "avl_archivo.dat"
    csv_path = "sales_dataset.csv"  # Asegúrate de que este archivo esté en la misma carpeta

    # Limpiar archivo si existe
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, "wb") as f:
        f.write(struct.pack("i", -1))  # raíz inicial -1

    avl = AVLFile(filename)

    print("\n=== CARGANDO VENTAS DESDE CSV ===")
    cargar_desde_csv(avl, csv_path)

    print("\n=== LECTURA DE TODOS LOS NODOS ===")
    for i in range(RECORDS_TO_PRINT):
        try:
            venta, altura, left, right = avl.read_node(i)
            print(f"[{i}] {venta} | Altura: {altura}, Left: {left}, Right: {right}")
        except:
            continue

    print("\n=== BÚSQUEDA POR ID ===")
    for id in [1, 3, 999]:
        print(f"Buscar ID {id}: {avl.search(id)}")

    print("\n=== BÚSQUEDA POR RANGO (1 a 5) ===")
    for venta in avl.search_range(1, 5):
        print(venta)

    print("\n=== ELIMINANDO ID 1 (si existe) ===")
    try:
        avl.remove(1)
        print("Eliminado correctamente.")
    except Exception as e:
        print(f"Error al eliminar: {e}")

    print("\n=== NODOS TRAS ELIMINACIÓN ===")
    for i in range(RECORDS_TO_PRINT):
        try:
            venta, altura, left, right = avl.read_node(i)
            print(f"[{i}] {venta} | Altura: {altura}, Left: {left}, Right: {right}")
        except:
            continue

    os.remove(filename)  # limpiar al final

if __name__ == "__main__":
    test_avl()
