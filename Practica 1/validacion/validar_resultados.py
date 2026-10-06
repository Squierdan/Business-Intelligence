import re
import sys
import warnings
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import xlrd

warnings.filterwarnings("ignore", category=UserWarning)

BASE = Path(__file__).resolve().parent.parent
ENTRADA = BASE / "datos" / "entrada" / "Caso Estudiantes Fechas Cedula.xls"
CATALOGO = BASE / "datos" / "entrada" / "catalogo_estados.csv"
SALIDA = BASE / "datos" / "salida"


def leer_fuente():
    hoja = xlrd.open_workbook(ENTRADA).sheet_by_name("Hoja1")
    filas = []
    for r in range(1, hoja.nrows):
        fila = []
        for c in range(hoja.ncols):
            if hoja.cell_type(r, c) == xlrd.XL_CELL_DATE:
                fila.append(xlrd.xldate_as_datetime(hoja.cell_value(r, c), hoja.book.datemode).date())
            else:
                fila.append(hoja.cell_value(r, c))
        filas.append(fila)
    columnas = ["ID", "NOMBRES", "APELLIDOS", "CEDULA", "MODALIDAD", "NIVEL",
                "FECHA_ADMISION", "ESTADO_ORIGINAL", "FECHA_ESTADO"]
    return pd.DataFrame(filas, columns=columnas)


def limpiar_nombre(valor):
    valor = valor.replace("||", "é").replace("~", "ñ")
    return re.sub(r"\s+", " ", valor).strip().upper()


def parsear_fecha(valor):
    if isinstance(valor, date):
        return valor
    texto = re.sub(r"^[^0-9]+", "", str(valor))
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})", texto)
    if m:
        return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
    m = re.match(r"^(\d{4})[/-](\d{1,2})[/-](\d{1,2})", texto)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def esperado():
    df = leer_fuente()
    catalogo = pd.read_csv(CATALOGO, sep=";", encoding="utf-8")
    homologacion = dict(zip(catalogo.ESTADO_ORIGEN, catalogo.ESTADO_ESTANDAR))

    df["NOMBRES"] = df.NOMBRES.map(limpiar_nombre)
    df["APELLIDOS"] = df.APELLIDOS.map(limpiar_nombre)
    df["CEDULA"] = df.CEDULA.map(lambda c: str(int(c)).zfill(10))
    df["MODALIDAD"] = df.MODALIDAD.str.upper().str.strip().str.replace(r"SEMI\s*PRESENCIAL", "SEMIPRESENCIAL", regex=True)
    df["NIVEL"] = df.NIVEL.str.upper().str.strip()
    df["ESTADO_ACTUAL"] = df.ESTADO_ORIGINAL.str.upper().str.strip().map(homologacion).fillna("NO HOMOLOGADO")
    df["FECHA_ADMISION"] = df.FECHA_ADMISION.map(parsear_fecha)
    df["FECHA_ESTADO"] = df.FECHA_ESTADO.map(parsear_fecha)
    df["DIAS_HASTA_ESTADO"] = (pd.to_datetime(df.FECHA_ESTADO) - pd.to_datetime(df.FECHA_ADMISION)).dt.days

    hoy = date.today()

    def motivo(f):
        if f.ESTADO_ACTUAL == "NO HOMOLOGADO":
            return "ESTADO NO EXISTE EN EL CATALOGO"
        if f.FECHA_ESTADO < f.FECHA_ADMISION:
            return "FECHA ESTADO ANTERIOR A FECHA ADMISION"
        if f.FECHA_ADMISION > hoy or f.FECHA_ESTADO > hoy:
            return "FECHA POSTERIOR A LA FECHA DE CARGA"
        if f.ESTADO_ACTUAL != "MATRICULADO" and f.DIAS_HASTA_ESTADO < 365:
            return "EGRESO O GRADUACION CON MENOS DE 365 DIAS DESDE LA ADMISION"
        return ""

    df["MOTIVO_OBSERVACION"] = df.apply(motivo, axis=1)
    return df


def normalizar(df):
    df = df.copy()
    for col in ("FECHA_ADMISION", "FECHA_ESTADO"):
        df[col] = pd.to_datetime(df[col]).dt.date
    df["CEDULA"] = df.CEDULA.astype(str).str.zfill(10)
    df["DIAS_HASTA_ESTADO"] = df.DIAS_HASTA_ESTADO.astype(int)
    return df.sort_values("ID").reset_index(drop=True)


def comparar(nombre, obtenido, referencia, columnas):
    obtenido = normalizar(obtenido)[columnas]
    referencia = normalizar(referencia)[columnas]
    if obtenido.shape != referencia.shape:
        print(f"[FALLA] {nombre}: {obtenido.shape[0]} filas obtenidas vs {referencia.shape[0]} esperadas")
        return False
    diferencias = (obtenido.astype(str) != referencia.astype(str)).any(axis=1)
    if diferencias.any():
        print(f"[FALLA] {nombre}: {int(diferencias.sum())} filas difieren")
        print(obtenido[diferencias].to_string())
        return False
    print(f"[OK] {nombre}: {len(obtenido)} filas coinciden campo por campo con el calculo independiente")
    return True


def main():
    ref = esperado()
    validos = ref[ref.MOTIVO_OBSERVACION == ""]
    observados = ref[ref.MOTIVO_OBSERVACION != ""]

    dw = pd.read_excel(SALIDA / "ESTUDIANTES_DW.xlsx", dtype={"CEDULA": str})
    obs = pd.read_excel(SALIDA / "REGISTROS_OBSERVADOS.xlsx", dtype={"CEDULA": str})
    resumen = pd.read_excel(SALIDA / "RESUMEN_VALIDACION.xlsx")
    guia = pd.read_excel(SALIDA / "SALIDA.xls")

    columnas = ["ID", "CEDULA", "NOMBRES", "APELLIDOS", "MODALIDAD", "NIVEL", "FECHA_ADMISION",
                "ESTADO_ACTUAL", "FECHA_ESTADO", "DIAS_HASTA_ESTADO"]
    resultados = [
        comparar("ESTUDIANTES_DW.xlsx", dw, validos, columnas),
        comparar("REGISTROS_OBSERVADOS.xlsx", obs, observados, columnas + ["MOTIVO_OBSERVACION"]),
    ]

    total = len(dw) + len(obs) + (len(pd.read_excel(SALIDA / "RECHAZOS_FORMATO_FECHA.xlsx"))
                                  if (SALIDA / "RECHAZOS_FORMATO_FECHA.xlsx").exists() else 0)
    print(f"[{'OK' if total == len(ref) else 'FALLA'}] Conciliacion: {len(ref)} filas de entrada = "
          f"{len(dw)} cargadas + {len(obs)} observadas + {total - len(dw) - len(obs)} rechazadas por formato")
    resultados.append(total == len(ref))

    duplicados = dw.ID.duplicated().sum()
    print(f"[{'OK' if duplicados == 0 else 'FALLA'}] IDs duplicados en ESTUDIANTES_DW: {duplicados}")
    resultados.append(duplicados == 0)

    conteo = dw.ESTADO_ACTUAL.value_counts().to_dict()
    cuadra = all(conteo.get(e, 0) == t for e, t in zip(resumen.ESTADO_ACTUAL, resumen.TOTAL_ESTUDIANTES))
    print(f"[{'OK' if cuadra else 'FALLA'}] RESUMEN_VALIDACION cuadra con el detalle: {dict(zip(resumen.ESTADO_ACTUAL, resumen.TOTAL_ESTUDIANTES))}")
    resultados.append(cuadra)

    estados_guia = sorted(guia["ESTADO ACTUAL"].unique())
    ok_guia = estados_guia == ["EGRESADO", "GRADUADO", "MATRICULADO"] and len(guia) == len(ref)
    print(f"[{'OK' if ok_guia else 'FALLA'}] SALIDA.xls de la guia: {len(guia)} filas, estados {estados_guia}")
    resultados.append(ok_guia)

    sys.exit(0 if all(resultados) else 1)


if __name__ == "__main__":
    main()
