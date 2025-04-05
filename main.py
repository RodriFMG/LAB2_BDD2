from BST.Venta import Venta
from BST.BSTFile import BSTFile

# 👇 importamos desde los archivos que YA TIENES
from SEQUENTIAL.venta_secuencial import VentaSecuencial
from SEQUENTIAL.sequential_file import (
    crear_archivo_secuencial,
    insertar_registro,
    buscar_por_id,
    eliminar_por_id,
    buscar_por_rango
)
import os

# ===============================
#      PARTE 1: ÁRBOL BST
# ===============================
if __name__ == "__main__":
    print("🌳 PRUEBA ÁRBOL BST")

    ventas = [
        Venta(2, "Producto B", 50, 29.99, "2023-04-02"),
        Venta(7, "Producto G", 75, 25.00, "2023-04-07"),
        Venta(3, "Producto D", 0, 39.99, "2023-04-04"),
        Venta(6, "Producto F", 120, 15.50, "2023-04-06"),
        Venta(9, "Producto I", 150, 12.99, "2023-04-09"),
        Venta(8, "Producto H", 10, 89.99, "2023-04-08"),
        Venta(10, "Producto J", 30, 35.99, "2023-04-10"),
    ]

    bst = BSTFile("./BST/binario.dat")

    # for venta in ventas:
    #     bst.Insert(venta)

    # bst.Remove(18)
    print(bst.ReadVenta(17))
    print("Root: ", bst.getRoot())

    # ===============================
    #      PARTE 2: ARCHIVO SECUENCIAL
    # ===============================
    print("\n📁 PRUEBA ARCHIVO SECUENCIAL")

    csv_path = "./sales_dataset.csv"
    crear_archivo_secuencial(csv_path)

    print("🟡 Insertando registro ID 1001")
    insertar_registro(1001, "Tablet Kawaii", 15, 999.99, "2025-04-04")

    print("🔍 Buscando registro ID 1001")
    venta = buscar_por_id(1001)
    if venta:
        venta()
    else:
        print("❌ No se encontró la venta.")

    print("❌ Eliminando registro ID 1001")
    eliminado = eliminar_por_id(1001)
    print("✅ Eliminado" if eliminado else "❌ No se pudo eliminar")

    print("🔍 Buscando registro ID 1001 luego de eliminar")
    venta = buscar_por_id(1001)
    if venta:
        venta()
    else:
        print("✅ Confirmado: registro no existe")

    print("📊 Buscando rango de ID 1 a 5")
    resultados = buscar_por_rango(1, 5)
    for r in resultados:
        r()

    print("📦 Verificando archivos:")
    print("sequential_file.dat:", os.path.exists("./SEQUENTIAL/sequential_file.dat"))
    print("aux_file.dat:", os.path.exists("./SEQUENTIAL/aux_file.dat"))


