import csv
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ENTRADA = BASE / "datos" / "entrada" / "ventas_1000.csv"
SALIDA = BASE / "datos" / "salida"

errores = []


def comprobar(condicion, mensaje):
    if not condicion:
        errores.append(mensaje)


def leer(nombre):
    with open(SALIDA / nombre, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


with open(ENTRADA, encoding="utf-8-sig", newline="") as f:
    ventas = list(csv.DictReader(f))

for v in ventas:
    v["quantity"] = int(v["quantity"])
    v["unit_price"] = Decimal(v["unit_price"])
    v["sales_amount"] = Decimal(v["sales_amount"])
    anio, mes, _ = v["order_date"].split("-")
    v["year"], v["month"] = int(anio), int(mes)

comprobar(len(ventas) == 1000, "raw_sales deberia tener 1000 filas")
comprobar(all(v["quantity"] * v["unit_price"] == v["sales_amount"] for v in ventas),
          "sales_amount no coincide con quantity * unit_price")


def unicos_consecutivos(campo):
    total, anterior = 0, None
    for v in ventas:
        if v[campo] != anterior:
            total += 1
        anterior = v[campo]
    return total


productos = {(v["product_id"], v["product_name"], v["category"], v["subcategory"]) for v in ventas}
clientes = {v["customer_id"] for v in ventas}
fechas = {v["order_date"] for v in ventas}

comprobar(len(productos) == 541, f"dim_product deberia tener 541 filas, hay {len(productos)}")
comprobar(len(clientes) == 100, f"dim_customer deberia tener 100 filas, hay {len(clientes)}")
comprobar(len(fechas) == 339, f"dim_date deberia tener 339 filas, hay {len(fechas)}")
comprobar(unicos_consecutivos("product_id") == 989, "Unique rows sin ordenar deberia dejar 989 productos")
comprobar(unicos_consecutivos("customer_id") == 990, "Unique rows sin ordenar deberia dejar 990 clientes")

categorias_por_producto = defaultdict(Counter)
for v in ventas:
    categorias_por_producto[v["product_id"]][v["category"]] += 1
moda = {p: c.most_common(1)[0][0] for p, c in categorias_por_producto.items()}
mal_asignadas = sum(1 for v in ventas if v["category"] != moda[v["product_id"]])
comprobar(len(categorias_por_producto) == 100, "deberia haber 100 product_id distintos")
comprobar(mal_asignadas == 562, f"con una categoria por product_id deberian cambiar 562 ventas, cambian {mal_asignadas}")

esperado = defaultdict(Decimal)
for v in ventas:
    esperado[(v["category"], v["month"])] += v["sales_amount"]
filas = leer("comprobacion_ventas_por_categoria_y_mes.csv")
comprobar(len(filas) == len(esperado), "la consulta de comprobacion no tiene el numero de filas esperado")
for f in filas:
    clave = (f["category"], int(f["month"]))
    comprobar(Decimal(f["total"]) == esperado.get(clave), f"comprobacion distinta en {clave}")

conteo, monto = Counter(), defaultdict(Decimal)
for v in ventas:
    clave = (v["year"], v["month"], v["category"])
    conteo[clave] += 1
    monto[clave] += v["sales_amount"]
filas = leer("consulta1_ventas_por_anio_mes_y_categoria.csv")
comprobar(len(filas) == len(conteo), "consulta 1 no tiene el numero de filas esperado")
for f in filas:
    clave = (int(f["year"]), int(f["month"]), f["category"])
    comprobar(int(f["numero_ventas"]) == conteo.get(clave), f"consulta 1: numero de ventas distinto en {clave}")
    comprobar(Decimal(f["total_vendido"]) == monto.get(clave), f"consulta 1: total distinto en {clave}")

por_cliente = defaultdict(Decimal)
genero_cliente = {}
for v in ventas:
    por_cliente[v["customer_id"]] += v["sales_amount"]
    genero_cliente[v["customer_id"]] = v["gender"]
filas = leer("consulta2_ventas_por_cliente_y_genero.csv")
comprobar(len(filas) == 100, "consulta 2 deberia tener 100 clientes")
for f in filas:
    comprobar(Decimal(f["total_vendido"]) == por_cliente[f["customer_id"]],
              f"consulta 2: total distinto para {f['customer_id']}")
    comprobar(f["gender"] == genero_cliente[f["customer_id"]], f"consulta 2: genero distinto para {f['customer_id']}")

por_genero = defaultdict(Decimal)
ventas_genero = Counter()
for v in ventas:
    por_genero[v["gender"]] += v["sales_amount"]
    ventas_genero[v["gender"]] += 1
for f in leer("consulta2b_ventas_por_genero.csv"):
    g = f["gender"]
    comprobar(Decimal(f["total_vendido"]) == por_genero[g], f"consulta 2b: total distinto para {g}")
    comprobar(int(f["numero_ventas"]) == ventas_genero[g], f"consulta 2b: ventas distintas para {g}")
    comprobar(int(f["clientes"]) == sum(1 for c in genero_cliente.values() if c == g),
              f"consulta 2b: clientes distintos para {g}")

for f in leer("conciliacion_ventas_por_categoria.csv"):
    comprobar(Decimal(f["diferencia"]) == 0, f"conciliacion con diferencia en {f['category']}")

total = sum(v["sales_amount"] for v in ventas)
unidades = sum(v["quantity"] for v in ventas)
print(f"raw_sales: {len(ventas)} filas, ventas {total}, unidades {unidades}")
print(f"dim_product: {len(productos)} filas para {len(categorias_por_producto)} product_id")
print(f"dim_customer: {len(clientes)} filas, dim_date: {len(fechas)} filas")
print(f"Unique rows sin ordenar: {unicos_consecutivos('product_id')} productos y {unicos_consecutivos('customer_id')} clientes")
print(f"Ventas que cambiarian de categoria con un solo registro por product_id: {mal_asignadas}")

if errores:
    print("Validacion con errores:")
    for e in errores:
        print(" -", e)
    sys.exit(1)
print("Validacion correcta")
