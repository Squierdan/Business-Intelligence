# Práctica 1: Implementación de un proceso ETL y Staging Area con Pentaho Data Integration

**Universidad:** Escuela Politécnica Nacional

**Facultad:** Facultad de Ingeniería de Sistemas

**Asignatura:** Business Intelligence

**Paralelo:** GR2SW

**Integrantes:**

- Elian Daniel Caizapanta Caiza
- Brandon Javier Pallo Chango
- Alexis Eduardo Sotomayor Llerena
- Francisco Javier Torres Negrete

**Fecha de entrega:** 13 de octubre de 2026

**Herramienta:** Pentaho Data Integration Community Edition 10.2.0.0-222 con Java 21

---

## Índice

1. [Organización del trabajo](#1-organización-del-trabajo)
2. [Parte 1: dataset de estudiantes](#2-parte-1-dataset-de-estudiantes)
   1. [Práctica guiada](#21-práctica-guiada)
   2. [Corrección de nombres y apellidos y validación de fechas](#22-corrección-de-nombres-y-apellidos-y-validación-de-fechas)
3. [Parte 2: proceso ETL con dos fuentes externas](#3-parte-2-proceso-etl-con-dos-fuentes-externas)
   1. [Objetivo del proceso](#31-objetivo-del-proceso)
   2. [Fuentes de datos utilizadas](#32-fuentes-de-datos-utilizadas)
   3. [Problemas encontrados en los datos](#33-problemas-encontrados-en-los-datos)
   4. [Transformaciones aplicadas](#34-transformaciones-aplicadas)
   5. [Flujo ETL desarrollado](#35-flujo-etl-desarrollado)
   6. [Evidencia del resultado](#36-evidencia-del-resultado)
   7. [Validación de los resultados](#37-validación-de-los-resultados)
   8. [Relación con la arquitectura de un Data Warehouse](#38-relación-con-la-arquitectura-de-un-data-warehouse)
4. [Conclusiones](#4-conclusiones)
5. [Referencias](#5-referencias)
6. [Declaración de uso de inteligencia artificial](#6-declaración-de-uso-de-inteligencia-artificial)

---

## 1. Organización del trabajo

La práctica tiene tres componentes: la transformación guiada realizada en clase, el punto 1 del trabajo grupal, que pide agregar dos transformaciones al dataset entregado por el docente, y el punto 2, que pide diseñar un proceso ETL completo con dos tipos diferentes de fuentes de datos [1]. Para que cada componente se pueda revisar por separado, el trabajo se dividió en dos partes, como se muestra en la Tabla 1.

**Tabla 1.** División del trabajo

| Parte | Qué cubre | Datos utilizados | Carpeta |
|---|---|---|---|
| Parte 1 | Práctica guiada y punto 1 del trabajo grupal | `Caso Estudiantes Fechas Cedula.xls`, entregado en clase | [parte1_estudiantes](parte1_estudiantes/) |
| Parte 2 | Punto 2 del trabajo grupal | Dos datasets públicos de ventas de cafeterías: un CSV con datos sucios y un libro de Excel | [parte2_ventas_cafeterias](parte2_ventas_cafeterias/) |

El dataset de estudiantes se usó únicamente para lo que la guía pide hacer sobre él. Para el punto 2 se buscaron fuentes externas reales, porque así el proceso enfrenta problemas de calidad que no fueron preparados para la clase y se puede demostrar la integración de dos formatos distintos en un mismo destino.

La Tabla 2 describe el contenido de cada carpeta del repositorio, con enlaces directos a cada carpeta y archivo. Todas las transformaciones leen y escriben con rutas relativas a partir de la variable `${Internal.Entry.Current.Directory}`, así que funcionan en cualquier equipo después de clonar el repositorio.

**Tabla 2.** Estructura del repositorio

| Parte | Carpeta | Archivos |
|---|---|---|
| Parte 1 | [Fuentes de datos](parte1_estudiantes/datos/entrada/) | [Caso Estudiantes Fechas Cedula.xls](parte1_estudiantes/datos/entrada/Caso%20Estudiantes%20Fechas%20Cedula.xls), [catalogo_estados.csv](parte1_estudiantes/datos/entrada/catalogo_estados.csv) |
| Parte 1 | [Salidas obtenidas](parte1_estudiantes/datos/salida/) | [SALIDA.xls](parte1_estudiantes/datos/salida/SALIDA.xls), [ESTUDIANTES_DW.xlsx](parte1_estudiantes/datos/salida/ESTUDIANTES_DW.xlsx), [REGISTROS_OBSERVADOS.xlsx](parte1_estudiantes/datos/salida/REGISTROS_OBSERVADOS.xlsx), [RESUMEN_VALIDACION.xlsx](parte1_estudiantes/datos/salida/RESUMEN_VALIDACION.xlsx) |
| Parte 1 | [Transformaciones](parte1_estudiantes/transformaciones/) | [01_ETL_Staging_Calidad.ktr](parte1_estudiantes/transformaciones/01_ETL_Staging_Calidad.ktr), [02_ETL_Estudiantes_Nombres_Fechas.ktr](parte1_estudiantes/transformaciones/02_ETL_Estudiantes_Nombres_Fechas.ktr) |
| Parte 1 | [Figuras](parte1_estudiantes/figuras/) | Figuras 1 a 6 del informe |
| Parte 1 | [Validación](parte1_estudiantes/validacion/) | [validar_resultados.py](parte1_estudiantes/validacion/validar_resultados.py) |
| Parte 2 | [Fuentes de datos](parte2_ventas_cafeterias/datos/entrada/) | [dirty_cafe_sales.csv](parte2_ventas_cafeterias/datos/entrada/dirty_cafe_sales.csv), [Coffee Shop Sales.xlsx](parte2_ventas_cafeterias/datos/entrada/Coffee%20Shop%20Sales.xlsx) |
| Parte 2 | [Salidas obtenidas](parte2_ventas_cafeterias/datos/salida/) | [VENTAS_CONSOLIDADAS.csv](parte2_ventas_cafeterias/datos/salida/VENTAS_CONSOLIDADAS.csv), [VENTAS_OBSERVADAS.xlsx](parte2_ventas_cafeterias/datos/salida/VENTAS_OBSERVADAS.xlsx), [RESUMEN_VENTAS.xlsx](parte2_ventas_cafeterias/datos/salida/RESUMEN_VENTAS.xlsx) |
| Parte 2 | [Transformaciones](parte2_ventas_cafeterias/transformaciones/) | [03_ETL_Ventas_Cafeterias.ktr](parte2_ventas_cafeterias/transformaciones/03_ETL_Ventas_Cafeterias.ktr) |
| Parte 2 | [Figuras](parte2_ventas_cafeterias/figuras/) | Figuras 8 a 13 del informe |
| Parte 2 | [Validación](parte2_ventas_cafeterias/validacion/) | [validar_resultados.py](parte2_ventas_cafeterias/validacion/validar_resultados.py) |

---

## 2. Parte 1: dataset de estudiantes

### 2.1. Práctica guiada

La transformación [01_ETL_Staging_Calidad.ktr](parte1_estudiantes/transformaciones/01_ETL_Staging_Calidad.ktr) reproduce los pasos de la guía [1]. El paso `Staging` lee el Excel, `CALIDAD DE DATOS` estandariza el estado académico con Replace in string y `Microsoft Excel writer` genera [SALIDA.xls](parte1_estudiantes/datos/salida/SALIDA.xls). Los reemplazos aplicados se listan en la Tabla 3. Se configuraron sin distinguir mayúsculas y por palabra completa, para que `EGR` no altere la palabra `EGRESADO`.

**Tabla 3.** Estandarización del estado académico

| Valor original | Valor estandarizado |
|---|---|
| Egresado, egresado, EGR, EGRESADA | EGRESADO |
| Graduado, graduado, GRD | GRADUADO |

La Figura 1 muestra la ejecución sin errores: `Staging` lee 99 filas y el escritor de Excel escribe 100, que corresponden a los 99 registros más el encabezado. El resultado tiene tres estados: 44 matriculados, 29 egresados y 26 graduados.

[![Ejecución de la transformación guiada](parte1_estudiantes/figuras/01_guia_ejecucion.jpg)](parte1_estudiantes/figuras/01_guia_ejecucion.jpg)

**Figura 1.** Ejecución de la transformación guiada en Spoon. Archivo: [01_guia_ejecucion.jpg](parte1_estudiantes/figuras/01_guia_ejecucion.jpg)

En la Figura 2 se ve la vista previa del paso `CALIDAD DE DATOS`. El estado ya aparece estandarizado, pero los nombres y las fechas todavía tienen los problemas que se corrigen en la sección siguiente, por ejemplo `Mu~oz`, `In||s` y `´12/06/2014`.

[![Vista previa de CALIDAD DE DATOS](parte1_estudiantes/figuras/02_guia_preview_calidad.jpg)](parte1_estudiantes/figuras/02_guia_preview_calidad.jpg)

**Figura 2.** Vista previa del paso CALIDAD DE DATOS. Archivo: [02_guia_preview_calidad.jpg](parte1_estudiantes/figuras/02_guia_preview_calidad.jpg)

### 2.2. Corrección de nombres y apellidos y validación de fechas

Antes de diseñar las transformaciones se revisaron los 99 registros del archivo [Caso Estudiantes Fechas Cedula.xls](parte1_estudiantes/datos/entrada/Caso%20Estudiantes%20Fechas%20Cedula.xls). La Tabla 4 resume los problemas encontrados.

**Tabla 4.** Problemas del dataset de estudiantes

| Problema | Ejemplos | Registros |
|---|---|---|
| Caracteres dañados en lugar de la letra é | `Jos\|\|`, `In\|\|s`, `Cort\|\|z` | 8 |
| Caracteres dañados en lugar de la letra ñ | `Mu~oz`, `Pe~a`, `Iba~ez` | 6 |
| Espacios sobrantes al final o dobles | `Cecilia `, `Biava  Gonzalez` | 9 |
| Uso irregular de mayúsculas | `fierro Muñoz`, `Romero benavente` | 10 |
| Fechas guardadas como texto | `01/01/2010 0:00` y `´12/06/2014` | 1 |
| Cédula sin el cero inicial | `500852125`, `95258652` | 2 |
| Estados que no concuerdan con las fechas | Graduados o egresados a los 50, 66 y 75 días de su admisión | 3 |

La fecha `´12/06/2014` se interpretó como 6 de diciembre de 2014, en formato mes, día y año. Es el mismo formato de la otra fecha en texto del registro y, con esa lectura, el registro L000101 queda con 1800 días entre admisión y estado, igual que L000102, que tiene exactamente las mismas fechas. También se detectaron dos posibles errores de digitación, `Flilomena` y `Vilalobos`, que no se modificaron porque un nombre propio solo debe corregirse después de confirmarlo con la fuente oficial.

La transformación [02_ETL_Estudiantes_Nombres_Fechas.ktr](parte1_estudiantes/transformaciones/02_ETL_Estudiantes_Nombres_Fechas.ktr) aplica los pasos de la Tabla 5. Todos son pasos estándar de Pentaho Data Integration [5].

**Tabla 5.** Pasos de la transformación de nombres y fechas

| Paso en Spoon | Tipo de paso | Función |
|---|---|---|
| Corregir nombres y apellidos | Replace in string | Reemplaza `\|\|` por é y `~` por ñ, reduce los espacios repetidos y unifica `Semi Presencial` como `SEMIPRESENCIAL` |
| Estandarizar texto | String operations | Quita espacios sobrantes y convierte a mayúsculas |
| Homologar estado con catalogo | Stream lookup | Cruza el estado con [catalogo_estados.csv](parte1_estudiantes/datos/entrada/catalogo_estados.csv) para obtener el valor oficial y su descripción |
| Limpiar formato de fechas | Replace in string | Quita caracteres extraños, pasa las fechas de mes/día/año a año/mes/día y descarta la hora |
| Validar formato de fechas | Filter rows | Envía a `RECHAZOS_FORMATO_FECHA.xlsx` las fechas que no se pudieron interpretar |
| Convertir tipos de fecha y cedula | Select values | Convierte las fechas a tipo fecha y la cédula a texto de 10 dígitos |
| Fecha de carga y Calcular dias hasta estado | Get system info y Calculator | Agregan la fecha de carga y los días entre admisión y estado |
| Regla 1 a Regla 4 | Filter rows | Validan que el estado exista, que la fecha de estado no sea anterior a la admisión, que no haya fechas futuras y que nadie egrese o se gradúe en menos de 365 días |

La Tabla 6 muestra algunos registros antes y después de la limpieza.

**Tabla 6.** Ejemplos de corrección en el dataset de estudiantes

| Antes | Después |
|---|---|
| `Sonia In\|\|s`, `Leal Leal` | `SONIA INÉS`, `LEAL LEAL` |
| `Jos\|\| Maria`, `fierro Mu~oz` | `JOSÉ MARIA`, `FIERRO MUÑOZ` |
| `500852125` | `0500852125` |
| `01/01/2010 0:00` y `´12/06/2014` | `2010-01-01` y `2014-12-06` |

El flujo completo se presenta en la Figura 3 y las métricas de ejecución en la Figura 4. De los 99 estudiantes, 96 pasan a [ESTUDIANTES_DW.xlsx](parte1_estudiantes/datos/salida/ESTUDIANTES_DW.xlsx) y 3 quedan en [REGISTROS_OBSERVADOS.xlsx](parte1_estudiantes/datos/salida/REGISTROS_OBSERVADOS.xlsx) porque figuran como graduados o egresados a los 50, 66 y 75 días de haber sido admitidos.

[![Flujo de la transformación de nombres y fechas](parte1_estudiantes/figuras/03_nombres_fechas_flujo.jpg)](parte1_estudiantes/figuras/03_nombres_fechas_flujo.jpg)

**Figura 3.** Flujo de la transformación de nombres y fechas ejecutado en Spoon. Archivo: [03_nombres_fechas_flujo.jpg](parte1_estudiantes/figuras/03_nombres_fechas_flujo.jpg)

[![Métricas por paso](parte1_estudiantes/figuras/04_nombres_fechas_metricas.jpg)](parte1_estudiantes/figuras/04_nombres_fechas_metricas.jpg)

**Figura 4.** Métricas por paso de la transformación de nombres y fechas. Archivo: [04_nombres_fechas_metricas.jpg](parte1_estudiantes/figuras/04_nombres_fechas_metricas.jpg)

La Figura 5 muestra la salida limpia, con tildes y eñes restituidas, cédula de 10 dígitos y fechas válidas. La Figura 6 muestra los tres registros observados con su motivo.

[![Vista previa de ESTUDIANTES_DW](parte1_estudiantes/figuras/05_nombres_fechas_preview_dw.jpg)](parte1_estudiantes/figuras/05_nombres_fechas_preview_dw.jpg)

**Figura 5.** Vista previa de la salida ESTUDIANTES_DW. Archivo: [05_nombres_fechas_preview_dw.jpg](parte1_estudiantes/figuras/05_nombres_fechas_preview_dw.jpg)

[![Vista previa de REGISTROS_OBSERVADOS](parte1_estudiantes/figuras/06_nombres_fechas_preview_observados.jpg)](parte1_estudiantes/figuras/06_nombres_fechas_preview_observados.jpg)

**Figura 6.** Vista previa de los registros observados del dataset de estudiantes. Archivo: [06_nombres_fechas_preview_observados.jpg](parte1_estudiantes/figuras/06_nombres_fechas_preview_observados.jpg)

Los resultados se verificaron con el script [validar_resultados.py](parte1_estudiantes/validacion/validar_resultados.py) de la Parte 1, que repite el procesamiento en Python a partir del Excel original. La Tabla 7 resume los controles.

**Tabla 7.** Validación de la Parte 1

| Control | Resultado |
|---|---|
| Filas de entrada frente a filas de salida | 99 = 96 cargadas + 3 observadas + 0 rechazadas |
| Coincidencia campo por campo con el cálculo independiente | 96 de 96 cargadas y 3 de 3 observadas |
| Identificadores duplicados | 0 |
| Registros válidos por estado según [RESUMEN_VALIDACION.xlsx](parte1_estudiantes/datos/salida/RESUMEN_VALIDACION.xlsx) | 44 matriculados, 28 egresados y 24 graduados |

---

## 3. Parte 2: proceso ETL con dos fuentes externas

### 3.1. Objetivo del proceso

Integrar en un solo conjunto de datos las ventas de dos cafeterías que registran su información en sistemas y formatos diferentes, limpiar los errores de origen, homologar los catálogos de productos y validar cada venta antes de cargarla, de modo que el resultado pueda alimentar un Data Mart de ventas. Este es el propósito central de la etapa de transformación en un Data Warehouse: limpiar, conformar y entregar datos confiables desde fuentes heterogéneas [3].

### 3.2. Fuentes de datos utilizadas

La Tabla 8 describe las dos fuentes. Ambas son públicas y se descargaron de copias publicadas en GitHub [8], [9].

**Tabla 8.** Fuentes de datos de la Parte 2

| Característica | Fuente 1 | Fuente 2 |
|---|---|---|
| Nombre | Cafe Sales, Dirty Data for Cleaning Training [6] | Coffee Shop Sales, Maven Roasters [7] |
| Publicado en | Kaggle | Maven Analytics Data Playground |
| Tipo de fuente | Archivo de texto CSV separado por comas | Libro de Excel `.xlsx`, hoja `Transactions` |
| Paso en PDI | CSV file input | Microsoft Excel input con el motor Excel 2007 XLSX Apache POI Streaming |
| Registros | 10 000 | 149 116 |
| Archivo en el repositorio | [dirty_cafe_sales.csv](parte2_ventas_cafeterias/datos/entrada/dirty_cafe_sales.csv) | [Coffee Shop Sales.xlsx](parte2_ventas_cafeterias/datos/entrada/Coffee%20Shop%20Sales.xlsx) |
| Periodo | Enero a diciembre de 2023 | Enero a junio de 2023 |
| Contenido | Producto, cantidad, precio unitario, total, método de pago, lugar de consumo y fecha | Fecha, hora, cantidad, local, producto, categoría, tipo y precio unitario de tres locales en Nueva York |

El CSV descargado se comparó con una segunda copia independiente y ambas tienen el mismo contenido byte por byte. Maven Analytics publica su dataset como dominio público [7].

### 3.3. Problemas encontrados en los datos

**Fuente 1, CSV de ventas.** De las 10 000 transacciones, 6 911 tienen al menos un campo dañado y solo 3 089 están completas. La Tabla 9 muestra cuántos valores inválidos tiene cada columna. Además, todas las columnas numéricas llegan como texto porque mezclan números con esas palabras.

**Tabla 9.** Valores inválidos por campo en la fuente 1

| Campo | Valor `ERROR` | Valor `UNKNOWN` | Vacío |
|---|---|---|---|
| Item | 292 | 344 | 333 |
| Quantity | 170 | 171 | 138 |
| Price Per Unit | 190 | 164 | 179 |
| Total Spent | 164 | 165 | 173 |
| Payment Method | 306 | 293 | 2 579 |
| Location | 358 | 338 | 3 265 |
| Transaction Date | 142 | 159 | 159 |

**Fuente 2, Excel de Maven Roasters.** Está mejor estructurado, pero no se puede integrar tal como viene. La Tabla 10 detalla sus problemas.

**Tabla 10.** Problemas de la fuente 2

| Problema | Detalle |
|---|---|
| Espacios sobrantes | 1 952 registros tienen espacios al final del nombre del producto, por ejemplo `Scottish Cream Scone ` |
| Tamaño mezclado en el nombre | 104 598 registros traen el tamaño pegado al nombre del producto: `Ethiopia Rg`, `Dark chocolate Lg`, `Columbian Medium Roast Sm` |
| Total ausente | No existe una columna con el total de la venta |
| Catálogo en inglés | Las nueve categorías y los tipos de producto están en inglés y no coinciden con los de la fuente 1 |
| Datos que la fuente no registra | No tiene método de pago ni lugar de consumo |

**Entre las dos fuentes.** Los nombres de columnas, los identificadores, el idioma y el nivel de detalle del producto son distintos: la fuente 1 vende ocho productos genéricos y la fuente 2 maneja 80 productos agrupados en 29 tipos.

### 3.4. Transformaciones aplicadas

La transformación [03_ETL_Ventas_Cafeterias.ktr](parte2_ventas_cafeterias/transformaciones/03_ETL_Ventas_Cafeterias.ktr) tiene tres bloques: limpieza y recuperación de la fuente 1, estandarización de la fuente 2, e integración y validación. Los pasos utilizados forman parte del catálogo estándar de Pentaho Data Integration [5].

La Tabla 11 lista los pasos aplicados a la fuente 1.

**Tabla 11.** Limpieza y recuperación de la fuente 1

| Paso en Spoon | Tipo de paso | Función |
|---|---|---|
| Anular valores invalidos | Replace in string | Convierte `ERROR` y `UNKNOWN` en valores vacíos para que se traten como nulos |
| Convertir tipos de dato | Select values | Convierte cantidad, precio y total a número y la fecha a tipo fecha |
| Registros con producto y precio, Catalogo precio por producto, Catalogo producto por precio | Filter rows y Memory group by | Construyen dos catálogos a partir de las ventas completas: el precio de lista de cada producto y los precios que corresponden a un solo producto |
| Buscar precio de lista y Recuperar precio | Stream lookup y User defined Java expression | Completan el precio usando el catálogo o, si el producto también falta, dividiendo el total para la cantidad |
| Buscar producto por precio y Recuperar valores faltantes | Stream lookup y User defined Java expression | Recuperan el producto a partir del precio cuando ese precio pertenece a un solo producto, y calculan la cantidad o el total que falten. La columna `CAMPOS_RECUPERADOS` deja constancia de lo que se completó |
| Traducir producto, Categoria del producto, Homologar canal, Homologar metodo de pago | Value mapper | Traducen los valores al español y asignan `NO REGISTRADO` cuando el dato no existe |

Los catálogos se construyen con los propios datos. En las ventas completas cada producto tiene un solo precio: café 2, té 1.5, galleta 1, ensalada 5, pastel y jugo 3, sánduche y batido 4. Los precios 1, 1.5, 2 y 5 identifican un único producto, así que se pueden usar para recuperarlo. Los precios 3 y 4 son compartidos y no permiten saber cuál fue el producto vendido. Con estas reglas se completaron datos en 1 682 ventas: 471 productos, 475 precios, 410 cantidades y 432 totales.

La Tabla 12 lista los pasos aplicados a la fuente 2.

**Tabla 12.** Estandarización de la fuente 2

| Paso en Spoon | Tipo de paso | Función |
|---|---|---|
| Quitar espacios y mayusculas | String operations | Elimina espacios sobrantes y pasa a mayúsculas local, categoría, tipo y producto |
| Separar tamano del producto | Replace in string con expresiones regulares | Separa el sufijo `SM`, `RG` o `LG` del nombre del producto |
| Traducir tamano y Traducir categoria | Value mapper | Convierten los tamaños en CHICO, MEDIANO y GRANDE, y las categorías al catálogo común en español |
| Calcular total de la venta | Calculator | Calcula el total como precio unitario por cantidad |
| Generar identificador | User defined Java expression | Antepone `MR-` al número de transacción para que no se confunda con los identificadores de la fuente 1 |

Cada fuente termina en un paso de selección que deja exactamente las mismas columnas con los mismos tipos. Después, `Unir ventas` junta los dos flujos y todas las ventas pasan por las mismas reglas:

1. El producto debe estar identificado.
2. Cantidad, precio y total deben tener valor.
3. La fecha debe ser válida.
4. El total debe ser igual a la cantidad por el precio, con una tolerancia de un centavo.

Las ventas que no cumplen una regla se envían a [VENTAS_OBSERVADAS.xlsx](parte2_ventas_cafeterias/datos/salida/VENTAS_OBSERVADAS.xlsx) con su motivo. Las demás se escriben en [VENTAS_CONSOLIDADAS.csv](parte2_ventas_cafeterias/datos/salida/VENTAS_CONSOLIDADAS.csv) y se resumen por origen y categoría en [RESUMEN_VENTAS.xlsx](parte2_ventas_cafeterias/datos/salida/RESUMEN_VENTAS.xlsx). Para que las dos fuentes se puedan analizar juntas, sus categorías se llevaron al catálogo común de la Tabla 13, que cumple el papel de una dimensión conformada [2].

**Tabla 13.** Catálogo común de categorías

| Categoría común | Fuente 1 | Fuente 2 |
|---|---|---|
| CAFE | Coffee | Coffee |
| TE | Tea | Tea |
| PANADERIA Y POSTRES | Cake, Cookie | Bakery |
| BEBIDAS FRIAS | Smoothie, Juice | No aplica |
| COMIDA PREPARADA | Sandwich, Salad | No aplica |
| CHOCOLATE CALIENTE | No aplica | Drinking Chocolate |
| SABORIZANTES | No aplica | Flavours |
| CAFE EN GRANO | No aplica | Coffee beans |
| TE A GRANEL | No aplica | Loose Tea |
| CHOCOLATE EMPACADO | No aplica | Packaged Chocolate |
| MERCANCIA DE MARCA | No aplica | Branded |

### 3.5. Flujo ETL desarrollado

La Figura 7 resume el flujo de forma conceptual. La fuente 1 pasa por la limpieza y la recuperación de valores, la fuente 2 por la estandarización, y ambas se unen antes de las reglas de validación.

```mermaid
flowchart LR
    F1[(Fuente 1: CSV ventas cafeteria)] --> L1[Anular valores invalidos]
    L1 --> L2[Convertir tipos de dato]
    L2 --> C1[Catalogos de precio y producto]
    L2 --> L3[Recuperar precio, producto, cantidad y total]
    C1 -.-> L3
    L3 --> L4[Traducir y homologar]
    L4 --> E1[Estructura comun]
    F2[(Fuente 2: Excel Maven Roasters)] --> M1[Quitar espacios y mayusculas]
    M1 --> M2[Separar tamano del producto]
    M2 --> M3[Traducir categoria y calcular total]
    M3 --> E2[Estructura comun]
    E1 --> U[Unir ventas]
    E2 --> U
    U --> V{Reglas 1 a 4}
    V -- no cumple --> OB[(VENTAS_OBSERVADAS.xlsx)]
    V -- cumple --> DW[(VENTAS_CONSOLIDADAS.csv)]
    DW --> RS[(RESUMEN_VENTAS.xlsx)]
```

**Figura 7.** Diagrama conceptual del flujo ETL de ventas

La Figura 8 muestra el mismo flujo construido en Spoon. La fuente 1 entra por la izquierda en la fila superior y la fuente 2 por la derecha en la fila inferior. Ambas se unen en `Unir ventas` y continúan por las reglas de validación.

[![Flujo del ETL de ventas en Spoon](parte2_ventas_cafeterias/figuras/01_flujo_etl_ventas.jpg)](parte2_ventas_cafeterias/figuras/01_flujo_etl_ventas.jpg)

**Figura 8.** Transformación 03_ETL_Ventas_Cafeterias en Spoon. Archivo: [01_flujo_etl_ventas.jpg](parte2_ventas_cafeterias/figuras/01_flujo_etl_ventas.jpg)

Para ejecutarlo se abre [03_ETL_Ventas_Cafeterias.ktr](parte2_ventas_cafeterias/transformaciones/03_ETL_Ventas_Cafeterias.ktr) en Spoon y se presiona Run. Desde la consola se usa Pan:

```bat
cd "D:\EPN\Septimo Semestre\Business Intelligence\Pentaho\data-integration"
Pan.bat /file:"D:\EPN\Septimo Semestre\Business Intelligence\Business-Intelligence\Practica 1\parte2_ventas_cafeterias\transformaciones\03_ETL_Ventas_Cafeterias.ktr" /level:Basic
```

La transformación tiene configurado un tamaño de buffer de 20 000 filas entre pasos. Es necesario porque el mismo flujo de la fuente 1 alimenta al catálogo y a la búsqueda de precios: si el buffer fuera menor que las 10 000 ventas, la búsqueda esperaría al catálogo y el catálogo nunca terminaría de recibir filas.

### 3.6. Evidencia del resultado

La Figura 9 muestra la ejecución completa en Spoon, que termina sin errores.

[![Ejecución del ETL de ventas](parte2_ventas_cafeterias/figuras/02_ejecucion_spoon.jpg)](parte2_ventas_cafeterias/figuras/02_ejecucion_spoon.jpg)

**Figura 9.** Ejecución de la transformación de ventas con su registro de eventos. Archivo: [02_ejecucion_spoon.jpg](parte2_ventas_cafeterias/figuras/02_ejecucion_spoon.jpg)

En la Figura 10 se ven las métricas por paso. Se leen 10 000 filas del CSV y 149 116 del Excel, se unen 159 116 y salen 158 180 consolidadas y 936 observadas.

[![Métricas por paso del ETL de ventas](parte2_ventas_cafeterias/figuras/03_metricas_pasos.jpg)](parte2_ventas_cafeterias/figuras/03_metricas_pasos.jpg)

**Figura 10.** Métricas por paso de la transformación de ventas. Archivo: [03_metricas_pasos.jpg](parte2_ventas_cafeterias/figuras/03_metricas_pasos.jpg)

La Figura 11 muestra ventas de Maven Roasters ya integradas, con la categoría traducida, el producto separado de su tamaño y el total calculado.

[![Vista previa de ventas de Maven Roasters](parte2_ventas_cafeterias/figuras/04_preview_ventas_maven.jpg)](parte2_ventas_cafeterias/figuras/04_preview_ventas_maven.jpg)

**Figura 11.** Vista previa de ventas consolidadas provenientes de Maven Roasters. Archivo: [04_preview_ventas_maven.jpg](parte2_ventas_cafeterias/figuras/04_preview_ventas_maven.jpg)

La Figura 12 muestra ventas de la cafetería después de la limpieza. La última columna indica qué valores se recuperaron. Las filas con `<null>` en producto son las que tienen precio 3 o 4 y no se pudieron identificar.

[![Vista previa de ventas de la cafetería](parte2_ventas_cafeterias/figuras/05_preview_ventas_cafeteria.jpg)](parte2_ventas_cafeterias/figuras/05_preview_ventas_cafeteria.jpg)

**Figura 12.** Vista previa de ventas de la cafetería después de la limpieza. Archivo: [05_preview_ventas_cafeteria.jpg](parte2_ventas_cafeterias/figuras/05_preview_ventas_cafeteria.jpg)

La Figura 13 muestra las ventas observadas con el motivo por el que no pasaron la validación.

[![Vista previa de ventas observadas](parte2_ventas_cafeterias/figuras/06_preview_ventas_observadas.jpg)](parte2_ventas_cafeterias/figuras/06_preview_ventas_observadas.jpg)

**Figura 13.** Vista previa de las ventas observadas. Archivo: [06_preview_ventas_observadas.jpg](parte2_ventas_cafeterias/figuras/06_preview_ventas_observadas.jpg)

La Tabla 14 resume los resultados por fuente y la Tabla 15 el resumen de ventas por categoría que genera el proceso en [RESUMEN_VENTAS.xlsx](parte2_ventas_cafeterias/datos/salida/RESUMEN_VENTAS.xlsx).

**Tabla 14.** Resultados del proceso por fuente

| Concepto | Fuente 1 CSV | Fuente 2 Excel | Total |
|---|---|---|---|
| Filas leídas | 10 000 | 149 116 | 159 116 |
| Ventas consolidadas | 9 064 | 149 116 | 158 180 |
| Observadas por producto no identificado | 480 | 0 | 480 |
| Observadas por montos sin valor recuperable | 20 | 0 | 20 |
| Observadas por fecha ausente o inválida | 436 | 0 | 436 |
| Observadas por total inconsistente | 0 | 0 | 0 |
| Monto vendido | 80 041.50 | 698 812.33 | 778 853.83 |

**Tabla 15.** Resumen de ventas por origen y categoría

| Origen | Categoría | Transacciones | Unidades | Ventas |
|---|---|---|---|---|
| CAFE SALES | COMIDA PREPARADA | 2 285 | 6 911 | 31 288.00 |
| CAFE SALES | BEBIDAS FRIAS | 2 167 | 6 535 | 22 799.00 |
| CAFE SALES | PANADERIA Y POSTRES | 2 230 | 6 705 | 13 261.00 |
| CAFE SALES | CAFE | 1 241 | 3 766 | 7 532.00 |
| CAFE SALES | TE | 1 141 | 3 441 | 5 161.50 |
| MAVEN ROASTERS | CAFE | 58 416 | 89 250 | 269 952.45 |
| MAVEN ROASTERS | TE | 45 449 | 69 737 | 196 405.95 |
| MAVEN ROASTERS | PANADERIA Y POSTRES | 22 796 | 23 214 | 82 315.64 |
| MAVEN ROASTERS | CHOCOLATE CALIENTE | 11 468 | 17 457 | 72 416.00 |
| MAVEN ROASTERS | CAFE EN GRANO | 1 753 | 1 828 | 40 085.25 |
| MAVEN ROASTERS | MERCANCIA DE MARCA | 747 | 776 | 13 607.00 |
| MAVEN ROASTERS | TE A GRANEL | 1 210 | 1 210 | 11 213.60 |
| MAVEN ROASTERS | SABORIZANTES | 6 790 | 10 511 | 8 408.80 |
| MAVEN ROASTERS | CHOCOLATE EMPACADO | 487 | 487 | 4 407.64 |

### 3.7. Validación de los resultados

Además de las reglas que aplica el propio ETL, el script [validar_resultados.py](parte2_ventas_cafeterias/validacion/validar_resultados.py) de la Parte 2 vuelve a procesar las dos fuentes originales en Python, sin usar nada de lo que generó Pentaho, y compara el resultado campo por campo con los archivos de salida. Se ejecutó sobre los archivos que produjo Spoon y los controles de la Tabla 16 resultaron correctos.

**Tabla 16.** Validación de la Parte 2

| Control | Resultado |
|---|---|
| Coincidencia de `VENTAS_CONSOLIDADAS.csv` con el cálculo independiente | 158 180 de 158 180 filas, campo por campo |
| Coincidencia de `VENTAS_OBSERVADAS.xlsx` con el cálculo independiente | 936 de 936 filas, incluido el motivo |
| Conciliación de filas | 159 116 leídas = 158 180 consolidadas + 936 observadas |
| Identificadores duplicados en la salida | 0 |
| Resumen frente al detalle | 14 combinaciones de origen y categoría con un total de 778 853.83 |

Para repetir la validación se ejecuta el script con Python y las librerías pandas, xlrd y openpyxl:

```bat
python "Practica 1\parte2_ventas_cafeterias\validacion\validar_resultados.py"
```

### 3.8. Relación con la arquitectura de un Data Warehouse

La Figura 14 ubica el proceso dentro de la arquitectura de un Data Warehouse, en la que los datos pasan de los sistemas fuente a una Staging Area, luego por la transformación y finalmente al almacén y a los Data Marts [4].

```mermaid
flowchart LR
    A[Sistemas fuente: CSV de ventas y Excel de Maven] --> B[Staging Area]
    B --> C[Limpieza, homologación y validación]
    C --> D[(Data Warehouse de ventas)]
    C --> Q[(Cuarentena: ventas observadas)]
    D --> E[Data Mart comercial]
    E --> F[Reportes y tableros]
```

**Figura 14.** Ubicación del proceso en la arquitectura de un Data Warehouse

Las dos cafeterías representan los sistemas operacionales de una empresa: cada una exporta sus ventas con su propio formato, idioma y nivel de calidad. Los pasos de lectura cumplen la función de Staging Area, porque reciben los datos tal como vienen, todo como texto en el caso del CSV, para no perder información antes de procesarla. En un entorno productivo esta área sería un conjunto de tablas temporales en la base de datos [3].

La etapa de transformación es donde se resuelven las diferencias. El catálogo común de categorías funciona como una dimensión conformada: las dos fuentes quedan clasificadas con los mismos valores, así que un reporte puede comparar el café vendido en ambas sin ajustes manuales [2]. La recuperación de valores con catálogos derivados de los propios datos es una regla de calidad documentada, y la columna `CAMPOS_RECUPERADOS` conserva el linaje de cada dato que no vino de origen.

Las ventas que no superan las reglas no se pierden ni contaminan el almacén: quedan en una salida de cuarentena con su motivo para que el área responsable las revise. Por tratarse de una práctica, la carga final se hace en archivos. En una solución real `VENTAS_CONSOLIDADAS` se cargaría con el paso Table output a una tabla de hechos.

Con estos datos se puede construir un modelo estrella [2] con una tabla de hechos de ventas, cuyas medidas serían cantidad, precio unitario y total, y las dimensiones fecha, producto con su categoría, detalle y tamaño, sucursal, canal de consumo, método de pago y origen. `RESUMEN_VENTAS.xlsx` es un primer ejemplo de las consultas que respondería el Data Mart.

---

## 4. Conclusiones

En la Parte 1, separar la lectura, la transformación y la carga permitió corregir los nombres y las fechas del dataset de estudiantes antes de llegar al destino. Las reglas de validación detectaron tres estudiantes con fechas que no tienen sentido para su estado académico.

En la Parte 2 se integraron dos fuentes reales con formatos distintos. Casi siete de cada diez registros del CSV tenían algún error. Gracias a los catálogos construidos con los propios datos se recuperó información en 1 682 ventas que de otra forma se habrían descartado, y solo 936 de 159 116 registros quedaron en observación.

Homologar las categorías en un catálogo común es lo que hace posible analizar juntas dos fuentes que no fueron diseñadas para integrarse.

La conciliación de conteos y la comparación con un cálculo independiente dan seguridad de que las salidas están completas y son correctas.

---

## 5. Referencias

[1] Escuela Politécnica Nacional, Facultad de Ingeniería de Sistemas, "Práctica 1. Implementación de un proceso ETL y Staging Area con Pentaho Data Integration," guía de práctica de la asignatura Business Intelligence, Quito, Ecuador, 2026.

[2] R. Kimball y M. Ross, *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling*, 3.ª ed. Indianapolis, IN, EE. UU.: Wiley, 2013.

[3] R. Kimball y J. Caserta, *The Data Warehouse ETL Toolkit: Practical Techniques for Extracting, Cleaning, Conforming, and Delivering Data*. Indianapolis, IN, EE. UU.: Wiley, 2004.

[4] P. Bhatia, *Data Mining and Data Warehousing: Principles and Practical Techniques*. Cambridge, Reino Unido: Cambridge University Press, 2019.

[5] Hitachi Vantara, "PDI transformation steps," *Pentaho Data Integration 10.2 Documentation*. [En línea]. Disponible en: https://docs.pentaho.com/pdia-data-integration/10.2-data-integration/pdi-transformation-steps-reference-overview. [Accedido: 13-oct-2026].

[6] ahmedmohamed2003, "Cafe Sales - Dirty Data for Cleaning Training," Kaggle, 2025. [En línea]. Disponible en: https://www.kaggle.com/datasets/ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training. [Accedido: 13-oct-2026].

[7] Maven Analytics, "Coffee Shop Sales," *Maven Analytics Data Playground*. [En línea]. Disponible en: https://mavenanalytics.io/data-playground/coffee-shop-sales. [Accedido: 13-oct-2026].

[8] Mehdi83, "cafe-sales-cleaning," repositorio de GitHub. [En línea]. Disponible en: https://github.com/Mehdi83/cafe-sales-cleaning. [Accedido: 13-oct-2026].

[9] Ayushi0214, "Datasets," repositorio de GitHub. [En línea]. Disponible en: https://github.com/Ayushi0214/Datasets. [Accedido: 13-oct-2026].

---

## 6. Declaración de uso de inteligencia artificial

En la elaboración de este trabajo se utilizó el asistente de inteligencia artificial Claude como apoyo en la redacción y el formato del informe en Markdown. El resto fue realizado por los estudiantes a cargo del informe.

**Porcentaje de uso de inteligencia artificial: 30 %**
