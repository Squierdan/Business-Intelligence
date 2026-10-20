import csv
import re
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "datos" / "entrada"
SALIDA = RAIZ / "datos" / "salida"

errores = []


def comprobar(condicion, mensaje):
    if not condicion:
        errores.append(mensaje)


def leer(ruta, delimitador, codificacion="utf-8-sig"):
    with open(ruta, newline="", encoding=codificacion) as f:
        return list(csv.reader(f, delimiter=delimitador))


def limpiar(texto):
    return re.sub(r"\s+", " ", texto).strip()


def parte1():
    filas = leer(ENTRADA / "products.csv", ",")[1:]
    comprobar(len(filas) == 699, "products.csv no tiene 699 registros")
    comprobar(len({f[0] for f in filas}) == 699, "products.csv no tiene 699 identificadores unicos")
    comprobar(len({f[2] for f in filas}) == 10, "products.csv no tiene 10 categorias")
    comprobar(len({f[3] for f in filas}) == 53, "products.csv no tiene 53 subcategorias")

    esperado = sorted(
        (f[0].strip(), limpiar(f[1]), f[2].strip(), f[3].strip()) for f in filas
    )
    dim = leer(SALIDA / "dim_product.csv", ";")[1:]
    obtenido = sorted((f[1], f[2], f[3], f[4]) for f in dim)
    comprobar(esperado == obtenido, "dim_product.csv difiere del calculo independiente")
    claves = [int(f[0]) for f in dim]
    comprobar(claves == list(range(1, 700)), "las claves sustitutas no son consecutivas de 1 a 699")
    comprobar(
        not any(re.search(r"\t|\s{2,}|^\s|\s$", f[2]) for f in dim),
        "dim_product.csv conserva tabulaciones o espacios sobrantes",
    )
    print(f"Parte 1: {len(dim)} productos, {len({f[3] for f in dim})} categorias, "
          f"{len({f[4] for f in dim})} subcategorias")


def cargar_ventas():
    filas = leer(ENTRADA / "Tabla_Desnormalizada_Ventas.csv", ";")
    cabecera, datos = filas[0], filas[1:]
    return [dict(zip(cabecera, f)) for f in datos if f]


def comparar(nombre, esperado, archivo):
    obtenido = [tuple(f) for f in leer(SALIDA / archivo, ";")[1:]]
    esperado = [tuple(str(x) for x in fila) for fila in esperado]
    comprobar(obtenido == esperado, f"{archivo} difiere del calculo independiente")
    print(f"  {nombre}: {len(obtenido)} filas")


def dos(valor):
    return f"{Decimal(valor):.2f}"


def parte2():
    v = cargar_ventas()
    comprobar(len(v) == 100, "la tabla desnormalizada no tiene 100 filas")
    comprobar(
        all(int(f["Quantity"]) * int(f["UnitPrice"]) == int(f["SalesAmount"]) for f in v),
        "hay filas con SalesAmount distinto de Quantity por UnitPrice",
    )
    comprobar(
        all(f["Ship Date"] >= f["Order Date"] for f in v),
        "hay ventas enviadas antes de la fecha de orden",
    )
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
             "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    print("Parte 2:")

    c1 = defaultdict(lambda: [set(), 0])
    c1b = defaultdict(lambda: [set(), 0])
    for f in v:
        anio, mes = int(f["Order Date"][:4]), int(f["Order Date"][5:7])
        for tabla, clave in ((c1, (anio, mes, f["Category"])), (c1b, (mes, f["Category"]))):
            tabla[clave][0].add(f["OrderNumber"])
            tabla[clave][1] += int(f["SalesAmount"])
    comparar(
        "consulta 1",
        [(a, m, meses[m - 1], c, len(t[0]), dos(t[1])) for (a, m, c), t in sorted(c1.items())],
        "consulta1_ventas_por_categoria_y_mes.csv",
    )
    comparar(
        "consulta 1b",
        [(m, meses[m - 1], c, len(t[0]), dos(t[1])) for (m, c), t in sorted(c1b.items())],
        "consulta1b_ventas_por_categoria_y_mes_del_anio.csv",
    )

    c2 = defaultdict(int)
    for f in v:
        c2[(int(f["CustomerKey"]), f["Gender"])] += int(f["SalesAmount"])
    comparar(
        "consulta 2",
        [(c, g, dos(t)) for (c, g), t in sorted(c2.items(), key=lambda x: -x[1])],
        "consulta2_ingreso_por_cliente_y_genero.csv",
    )

    c3 = defaultdict(int)
    nombres = {}
    for f in v:
        c3[int(f["ProductKey"])] += int(f["Quantity"])
        nombres[int(f["ProductKey"])] = f["Product Name"]
    comparar(
        "consulta 3",
        [(p, nombres[p], t) for p, t in sorted(c3.items(), key=lambda x: (-x[1], x[0]))],
        "consulta3_cantidad_por_producto.csv",
    )

    c4 = defaultdict(int)
    c4b = defaultdict(int)
    for f in v:
        anio, mes = int(f["Ship Date"][:4]), int(f["Ship Date"][5:7])
        c4[(anio, mes)] += int(f["Quantity"])
        c4b[mes] += int(f["Quantity"])
    comparar(
        "consulta 4",
        [(a, m, meses[m - 1], t) for (a, m), t in sorted(c4.items())],
        "consulta4_cantidad_enviada_por_mes_de_envio.csv",
    )
    comparar(
        "consulta 4b",
        [(m, meses[m - 1], t) for m, t in sorted(c4b.items())],
        "consulta4b_cantidad_enviada_por_mes_del_anio.csv",
    )

    c5 = defaultdict(lambda: [0, 0])
    for f in v:
        c5[(f["Size"], f["Marital Status"])][0] += int(f["SalesAmount"])
        c5[(f["Size"], f["Marital Status"])][1] += int(f["Quantity"])
    orden = {"Small": 1, "Medium": 2, "Large": 3}
    comparar(
        "consulta 5",
        [(s, e, dos(t[0]), t[1]) for (s, e), t in sorted(c5.items(), key=lambda x: (orden[x[0][0]], x[0][1]))],
        "consulta5_ventas_por_tamano_y_estado_civil.csv",
    )

    total = sum(int(f["SalesAmount"]) for f in v)
    unidades = sum(int(f["Quantity"]) for f in v)
    print(f"  ventas totales {total}, unidades {unidades}")


parte1()
parte2()

if errores:
    print("Validacion con errores:")
    for e in errores:
        print(" -", e)
    sys.exit(1)
print("Validacion correcta")
