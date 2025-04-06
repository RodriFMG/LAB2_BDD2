import time
import pandas as pd
import os
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

# Leer CSV
df = pd.read_csv(csv_path)

# Crear archivo secuencial inicial con 1000 registros y medir tiempo
tiempo_csv_insert = []
df_ordenado = df.sort_values(by="ID de la venta")
os.makedirs("../SEQUENTIAL", exist_ok=True)
with open(main_file_path, "wb") as f:
    for _, row in df_ordenado.iterrows():
        start = time.time()
        insertar_registro(int(row["ID de la venta"]),
                          row["Nombre producto"],
                          int(row["Cantidad vendida"]),
                          float(row["Precio unitario"]),
                          row["Fecha de venta"])
        end = time.time()
        tiempo_csv_insert.append(end - start)
# Crear archivo auxiliar vacío
open(aux_file_path, "wb").close()

# Insertar log(1000) = 10 registros adicionales y medir tiempo
tiempo_insert = []
for i in range(1000, 1009):
    row = df.iloc[i % 1000]  # Reutilizamos registros existentes
    start = time.time()
    insertar_registro(int(row["ID de la venta"]) + 1000,  # Asegurar ID único
                      row["Nombre producto"],
                      int(row["Cantidad vendida"]),
                      float(row["Precio unitario"]),
                      row["Fecha de venta"])
    end = time.time()
    tiempo_insert.append(end - start)

# Buscar ID existente
start = time.time()
buscar_por_id(1000)  # Asegurar que existe
end = time.time()
tiempo_busqueda = end - start

# Eliminar ID existente
start = time.time()
eliminar_por_id(1000)
end = time.time()
tiempo_eliminacion = end - start

# Buscar por rango
start = time.time()
buscar_por_rango(1, 1000)
end = time.time()
tiempo_rango = end - start

# Mostrar resultados
print(f"Tiempo promedio de inserción (1000 registros CSV): {sum(tiempo_csv_insert)/len(tiempo_csv_insert):.6f} segundos")
print(f"Tiempo promedio de inserción (10 registros extra): {sum(tiempo_insert)/len(tiempo_insert):.6f} segundos")
print(f"Tiempo de búsqueda por ID: {tiempo_busqueda:.6f} segundos")
print(f"Tiempo de eliminación por ID: {tiempo_eliminacion:.6f} segundos")
print(f"Tiempo de búsqueda por rango: {tiempo_rango:.6f} segundos")

