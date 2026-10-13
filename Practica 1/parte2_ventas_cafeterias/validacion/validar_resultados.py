import sys
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)

BASE = Path(__file__).resolve().parent.parent
ENTRADA = BASE / "datos" / "entrada"
SALIDA = BASE / "datos" / "salida"

PRODUCTOS = {"Coffee": "CAFE", "Tea": "TE", "Sandwich": "SANDUCHE", "Salad": "ENSALADA",
             "Cake": "PASTEL", "Cookie": "GALLETA", "Smoothie": "BATIDO", "Juice": "JUGO"}
CATEGORIAS_CAFE = {"Coffee": "CAFE", "Tea": "TE", "Sandwich": "COMIDA PREPARADA", "Salad": "COMIDA PREPARADA",
                   "Cake": "PANADERIA Y POSTRES", "Cookie": "PANADERIA Y POSTRES",
                   "Smoothie": "BEBIDAS FRIAS", "Juice": "BEBIDAS FRIAS"}
CATEGORIAS_MAVEN = {"COFFEE": "CAFE", "TEA": "TE", "DRINKING CHOCOLATE": "CHOCOLATE CALIENTE",
                    "BAKERY": "PANADERIA Y POSTRES", "FLAVOURS": "SABORIZANTES", "COFFEE BEANS": "CAFE EN GRANO",
                    "LOOSE TEA": "TE A GRANEL", "PACKAGED CHOCOLATE": "CHOCOLATE EMPACADO",
                    "BRANDED": "MERCANCIA DE MARCA"}
CANALES = {"In-store": "EN LOCAL", "Takeaway": "PARA LLEVAR"}
PAGOS = {"Cash": "EFECTIVO", "Credit Card": "TARJETA DE CREDITO", "Digital Wallet": "BILLETERA DIGITAL"}
TAMANOS = {"SM": "CHICO", "RG": "MEDIANO", "LG": "GRANDE"}
COLUMNAS = ["ORIGEN", "FECHA", "SUCURSAL", "CANAL", "METODO_PAGO", "CATEGORIA", "PRODUCTO", "DETALLE",
            "TAMANO", "CANTIDAD", "PRECIO_UNITARIO", "TOTAL"]


def esperado_cafe():
    df = pd.read_csv(ENTRADA / "dirty_cafe_sales.csv", dtype=str, keep_default_na=False)
    df = df.apply(lambda c: c.str.strip()).replace({"ERROR": None, "UNKNOWN": None, "": None})
    item = df["Item"]
    cantidad = pd.to_numeric(df["Quantity"])
    precio = pd.to_numeric(df["Price Per Unit"])
    total = pd.to_numeric(df["Total Spent"])
    fecha = pd.to_datetime(df["Transaction Date"], format="%Y-%m-%d", errors="coerce")

    completos = pd.DataFrame({"item": item, "precio": precio}).dropna()
    lista = completos.groupby("item")["precio"].max()
    por_precio = completos.groupby("precio")["item"].agg(lambda s: s.iloc[0] if s.nunique() == 1 else None).dropna()

    precio_f = precio.copy()
    falta = precio_f.isna()
    precio_f[falta] = item[falta].map(lista)
    falta = precio_f.isna() & total.notna() & cantidad.notna() & (cantidad > 0)
    precio_f[falta] = total[falta] / cantidad[falta]

    item_f = item.copy()
    falta = item_f.isna()
    item_f[falta] = precio_f[falta].map(por_precio)

    cantidad_f = cantidad.copy()
    falta = cantidad_f.isna() & total.notna() & precio_f.notna() & (precio_f > 0)
    cantidad_f[falta] = (total[falta] / precio_f[falta]).round()

    total_f = total.copy()
    falta = total_f.isna() & cantidad_f.notna() & precio_f.notna()
    total_f[falta] = cantidad_f[falta] * precio_f[falta]

    salida = pd.DataFrame({
        "ID_TRANSACCION": df["Transaction ID"],
        "ORIGEN": "CAFE SALES",
        "FECHA": fecha.dt.date,
        "SUCURSAL": "LOCAL UNICO",
        "CANAL": df["Location"].map(CANALES).fillna("NO REGISTRADO"),
        "METODO_PAGO": df["Payment Method"].map(PAGOS).fillna("NO REGISTRADO"),
        "CATEGORIA": item_f.map(CATEGORIAS_CAFE),
        "PRODUCTO": item_f.map(PRODUCTOS),
        "DETALLE": item_f.map(PRODUCTOS),
        "TAMANO": "UNICO",
        "CANTIDAD": cantidad_f,
        "PRECIO_UNITARIO": precio_f,
        "TOTAL": total_f,
    })

    def motivo(f):
        if pd.isna(f.PRODUCTO):
            return "NO SE PUDO IDENTIFICAR EL PRODUCTO"
        if pd.isna(f.CANTIDAD) or pd.isna(f.PRECIO_UNITARIO) or pd.isna(f.TOTAL):
            return "CANTIDAD PRECIO O TOTAL SIN VALOR RECUPERABLE"
        if pd.isna(f.FECHA):
            return "FECHA AUSENTE O INVALIDA"
        if abs(f.TOTAL - f.CANTIDAD * f.PRECIO_UNITARIO) > 0.01:
            return "TOTAL NO COINCIDE CON CANTIDAD POR PRECIO"
        return ""

    salida["MOTIVO_OBSERVACION"] = salida.apply(motivo, axis=1)
    return salida


def esperado_maven():
    df = pd.read_excel(ENTRADA / "Coffee Shop Sales.xlsx", sheet_name="Transactions")
    detalle = df["product_detail"].str.strip().str.upper()
    tamano = detalle.str.extract(r"\s(SM|RG|LG)$")[0]
    return pd.DataFrame({
        "ID_TRANSACCION": "MR-" + df["transaction_id"].astype(str),
        "ORIGEN": "MAVEN ROASTERS",
        "FECHA": df["transaction_date"].dt.date,
        "SUCURSAL": df["store_location"].str.strip().str.upper(),
        "CANAL": "NO REGISTRADO",
        "METODO_PAGO": "NO REGISTRADO",
        "CATEGORIA": df["product_category"].str.strip().str.upper().map(CATEGORIAS_MAVEN),
        "PRODUCTO": df["product_type"].str.strip().str.upper(),
        "DETALLE": detalle.str.replace(r"\s+(SM|RG|LG)$", "", regex=True),
        "TAMANO": tamano.map(TAMANOS).fillna("UNICO"),
        "CANTIDAD": df["transaction_qty"],
        "PRECIO_UNITARIO": df["unit_price"],
        "TOTAL": df["transaction_qty"] * df["unit_price"],
        "MOTIVO_OBSERVACION": "",
    })


def normalizar(df):
    df = df.copy()
    df["FECHA"] = pd.to_datetime(df["FECHA"]).dt.strftime("%Y-%m-%d")
    df["CANTIDAD"] = pd.to_numeric(df["CANTIDAD"]).round().astype("Int64").astype(str)
    for col in ("PRECIO_UNITARIO", "TOTAL"):
        df[col] = pd.to_numeric(df[col]).map(lambda v: f"{v:.2f}")
    return df.set_index("ID_TRANSACCION").sort_index()


def comparar(nombre, obtenido, referencia, columnas):
    if len(obtenido) != len(referencia):
        print(f"[FALLA] {nombre}: {len(obtenido)} filas obtenidas frente a {len(referencia)} esperadas")
        return False
    a = normalizar(obtenido)[columnas]
    b = normalizar(referencia)[columnas]
    if not a.index.equals(b.index):
        print(f"[FALLA] {nombre}: los identificadores no coinciden")
        return False
    distintas = (a.astype(str) != b.astype(str)).any(axis=1)
    if distintas.any():
        print(f"[FALLA] {nombre}: {int(distintas.sum())} filas con diferencias")
        print(pd.concat([a[distintas].head(5), b[distintas].head(5)], keys=["obtenido", "esperado"]).to_string())
        return False
    print(f"[OK] {nombre}: {len(a)} filas coinciden campo por campo con el calculo independiente")
    return True


def main():
    ref = pd.concat([esperado_cafe(), esperado_maven()], ignore_index=True)
    validas = ref[ref.MOTIVO_OBSERVACION == ""]
    observadas = ref[ref.MOTIVO_OBSERVACION != ""]

    consolidadas = pd.read_csv(SALIDA / "VENTAS_CONSOLIDADAS.csv", sep=";", dtype=str, keep_default_na=False)
    obs = pd.read_excel(SALIDA / "VENTAS_OBSERVADAS.xlsx", dtype={"ID_TRANSACCION": str, "MOTIVO_OBSERVACION": str})
    resumen = pd.read_excel(SALIDA / "RESUMEN_VENTAS.xlsx")

    resultados = [
        comparar("VENTAS_CONSOLIDADAS.csv", consolidadas, validas, COLUMNAS),
        comparar("VENTAS_OBSERVADAS.xlsx", obs, observadas, ["ORIGEN", "MOTIVO_OBSERVACION"]),
    ]

    leidas = len(ref)
    cuadra = leidas == len(consolidadas) + len(obs)
    print(f"[{'OK' if cuadra else 'FALLA'}] Conciliacion: {leidas} filas leidas = "
          f"{len(consolidadas)} consolidadas + {len(obs)} observadas")
    resultados.append(cuadra)

    duplicados = int(consolidadas.ID_TRANSACCION.duplicated().sum())
    print(f"[{'OK' if duplicados == 0 else 'FALLA'}] Identificadores duplicados en la salida: {duplicados}")
    resultados.append(duplicados == 0)

    agrupado = validas.groupby(["ORIGEN", "CATEGORIA"]).agg(TRANSACCIONES=("TOTAL", "size"), VENTAS=("TOTAL", "sum"))
    resumen = resumen.set_index(["ORIGEN", "CATEGORIA"]).sort_index()
    agrupado = agrupado.sort_index()
    cuadra_resumen = (resumen.index.equals(agrupado.index)
                      and (resumen.TRANSACCIONES.values == agrupado.TRANSACCIONES.values).all()
                      and ((resumen.VENTAS.values - agrupado.VENTAS.values).__abs__() < 0.01).all())
    print(f"[{'OK' if cuadra_resumen else 'FALLA'}] RESUMEN_VENTAS cuadra con el detalle: "
          f"{len(resumen)} combinaciones de origen y categoria, ventas totales {resumen.VENTAS.sum():,.2f}")
    resultados.append(cuadra_resumen)

    sys.exit(0 if all(resultados) else 1)


if __name__ == "__main__":
    main()
