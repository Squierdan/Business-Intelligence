import csv
import re
import sys
from pathlib import Path

base = Path(__file__).resolve().parent.parent
entrada = base / "datos" / "entrada" / "productos_ferreteria_raw.csv"
salida = base / "datos" / "salida" / "productos_ferreteria_clean.csv"

CATEGORIAS = {
    "herramientas": "Herramientas", "herramienta": "Herramientas", "herram.": "Herramientas",
    "htas": "Herramientas", "htas.": "Herramientas",
    "pinturas": "Pinturas", "pintura": "Pinturas", "pint": "Pinturas", "pint.": "Pinturas",
    "ferreteria": "Ferretería", "ferretería": "Ferretería", "ferre": "Ferretería",
    "fontaneria": "Fontanería", "fontanería": "Fontanería",
    "electricidad": "Electricidad", "electric.": "Electricidad", "electr.": "Electricidad",
    "seguridad": "Seguridad",
    "adhesivos": "Adhesivos", "adhesivo": "Adhesivos",
    "selladores": "Selladores", "sellador": "Selladores",
}
UNIDADES = {
    "und": "UND", "unidad": "UND", "u": "UND",
    "l": "L", "lt": "L", "litro": "L",
    "rollo": "ROLLO", "rl": "ROLLO",
    "caja": "CAJA", "cj": "CAJA",
    "tubo": "TUBO", "frasco": "FRASCO", "hoja": "HOJA", "par": "PAR", "set": "SET",
    "m": "M", "mt": "M", "metro": "M",
}


def limpiar(fila):
    categoria = CATEGORIAS[fila["categoria"].strip().lower()]
    texto = fila["unidad_medida"].strip().lower()
    m = re.fullmatch(r"(\d+)\s*([a-z]+)", texto)
    if m:
        cantidad, unidad = m.group(1), m.group(2)
    else:
        cantidad, unidad = "1", texto
    precio = fila["precio_unitario"].replace("$", "").strip()
    return [fila["id_producto"], fila["nombre_producto"], categoria, cantidad,
            UNIDADES[unidad], precio, fila["proveedor"]]


with open(entrada, encoding="utf-8", newline="") as f:
    origen = list(csv.DictReader(f, delimiter=";"))
esperadas = [limpiar(fila) for fila in origen]

with open(salida, encoding="utf-8", newline="") as f:
    lector = csv.reader(f, delimiter=";")
    cabecera = next(lector)
    obtenidas = [fila for fila in lector]

errores = []
if len(obtenidas) != len(esperadas):
    errores.append(f"filas esperadas {len(esperadas)} y obtenidas {len(obtenidas)}")
for e, o in zip(esperadas, obtenidas):
    if e[:5] != o[:5] or float(e[5]) != float(o[5]) or e[6] != o[6]:
        errores.append(f"esperado {e} y obtenido {o}")
if any("$" in fila[5] for fila in obtenidas):
    errores.append("quedan simbolos de moneda")

print(f"Filas de origen: {len(origen)}")
print(f"Filas cargadas: {len(obtenidas)}")
print(f"Categorias distintas antes: {len({r['categoria'] for r in origen})}")
print(f"Categorias distintas despues: {len({r[2] for r in obtenidas})}")
print(f"Unidades distintas antes: {len({r['unidad_medida'] for r in origen})}")
print(f"Unidades distintas despues: {len({r[4] for r in obtenidas})}")
if errores:
    print("ERRORES")
    for e in errores:
        print(" ", e)
    sys.exit(1)
print("Validacion correcta")
