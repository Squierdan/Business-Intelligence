import csv
import sys
from pathlib import Path

base = Path(__file__).resolve().parent.parent
entrada = base / "datos" / "entrada" / "dim_production.sql"
salida = base / "datos" / "salida" / "dim_production_new.csv"

filas_origen = []
for linea in entrada.read_text(encoding="utf-8").splitlines():
    linea = linea.strip()
    if linea.startswith("('P"):
        partes = [p.strip().strip("'") for p in linea.rstrip(",;").strip("()").split("', '")]
        filas_origen.append(partes)

esperadas = [[f[0], f[1].replace("24", "25"), f[2], f[3]] for f in filas_origen]

with open(salida, encoding="utf-8", newline="") as f:
    lector = csv.reader(f, delimiter=";")
    next(lector)
    obtenidas = [fila for fila in lector]

errores = []
if len(obtenidas) != len(esperadas):
    errores.append(f"filas esperadas {len(esperadas)} y obtenidas {len(obtenidas)}")
for e, o in zip(esperadas, obtenidas):
    if e != o:
        errores.append(f"esperado {e} y obtenido {o}")

print(f"Filas de origen: {len(filas_origen)}")
print(f"Filas cargadas: {len(obtenidas)}")
print(f"Productos con 24 reemplazado por 25: {sum(1 for e, f in zip(esperadas, filas_origen) if e != f)}")
if errores:
    print("ERRORES")
    for e in errores:
        print(" ", e)
    sys.exit(1)
print("Validacion correcta")
