SELECT COUNT(*)                          AS filas,
       COUNT(DISTINCT order_number)      AS ordenes,
       COUNT(DISTINCT productkey)        AS productos,
       COUNT(DISTINCT customerkey)       AS clientes,
       COUNT(DISTINCT orderdatekey)      AS fechas_de_orden,
       COUNT(DISTINCT shipdatekey)       AS fechas_de_envio
FROM dw_ventas.stg_ventas;

UPDATE dw_ventas.stg_ventas
SET productkey        = btrim(productkey),
    product_code      = btrim(product_code),
    product_name      = btrim(regexp_replace(product_name, '\s+', ' ', 'g')),
    list_price        = btrim(list_price),
    color             = btrim(color),
    size              = btrim(size),
    category          = btrim(category),
    subcategory       = btrim(subcategory),
    customerkey       = btrim(customerkey),
    birth_date        = btrim(birth_date),
    marital_status    = btrim(marital_status),
    gender            = upper(btrim(gender)),
    income            = btrim(income),
    children          = btrim(children),
    home_owner        = btrim(home_owner),
    cars              = btrim(cars),
    orderdatekey      = btrim(orderdatekey),
    order_date        = btrim(order_date),
    shipdatekey       = btrim(shipdatekey),
    ship_date         = btrim(ship_date),
    order_number      = btrim(order_number),
    order_line_number = btrim(order_line_number),
    quantity          = btrim(quantity),
    unit_price        = btrim(unit_price),
    product_cost      = btrim(product_cost),
    sales_amount      = btrim(sales_amount);

SELECT COUNT(*) FILTER (WHERE order_number IS NULL OR order_number = '')                         AS orden_vacia,
       COUNT(*) FILTER (WHERE productkey IS NULL OR customerkey IS NULL)                         AS claves_nulas,
       COUNT(*) FILTER (WHERE quantity::INTEGER * unit_price::NUMERIC <> sales_amount::NUMERIC)  AS importe_inconsistente,
       COUNT(*) FILTER (WHERE ship_date::DATE < order_date::DATE)                                AS envio_antes_de_orden,
       COUNT(*) FILTER (WHERE orderdatekey <> to_char(order_date::DATE, 'YYYYMMDD'))             AS clave_de_orden_distinta,
       COUNT(*) FILTER (WHERE shipdatekey <> to_char(ship_date::DATE, 'YYYYMMDD'))               AS clave_de_envio_distinta
FROM dw_ventas.stg_ventas;

SELECT order_number, order_line_number, COUNT(*)
FROM dw_ventas.stg_ventas
GROUP BY order_number, order_line_number
HAVING COUNT(*) > 1;

INSERT INTO dw_ventas.dim_product
    (product_id, product_code, product_name, list_price, color, size, category, subcategory)
SELECT DISTINCT
    productkey::INTEGER,
    product_code,
    product_name,
    list_price::NUMERIC,
    color,
    size,
    category,
    subcategory
FROM dw_ventas.stg_ventas
ORDER BY productkey::INTEGER;

INSERT INTO dw_ventas.dim_customer
    (customer_id, birth_date, marital_status, gender, income, children, home_owner, cars)
SELECT DISTINCT
    customerkey::INTEGER,
    birth_date::DATE,
    marital_status,
    gender,
    income::NUMERIC,
    children::SMALLINT,
    home_owner,
    cars::SMALLINT
FROM dw_ventas.stg_ventas
ORDER BY customerkey::INTEGER;

INSERT INTO dw_ventas.dim_date
    (date_key, full_date, year, quarter, month, month_name, year_month, day, day_of_week, day_name, is_weekend)
SELECT
    to_char(d, 'YYYYMMDD')::INTEGER,
    d::DATE,
    EXTRACT(YEAR FROM d),
    EXTRACT(QUARTER FROM d),
    EXTRACT(MONTH FROM d),
    (ARRAY['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto',
           'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'])[EXTRACT(MONTH FROM d)::INTEGER],
    to_char(d, 'YYYY-MM'),
    EXTRACT(DAY FROM d),
    EXTRACT(ISODOW FROM d),
    (ARRAY['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo'])[EXTRACT(ISODOW FROM d)::INTEGER],
    EXTRACT(ISODOW FROM d) >= 6
FROM generate_series(
    (SELECT date_trunc('year', LEAST(MIN(order_date::DATE), MIN(ship_date::DATE))) FROM dw_ventas.stg_ventas),
    (SELECT date_trunc('year', GREATEST(MAX(order_date::DATE), MAX(ship_date::DATE))) + INTERVAL '1 year - 1 day' FROM dw_ventas.stg_ventas),
    INTERVAL '1 day'
) AS g(d);

INSERT INTO dw_ventas.fact_sales
    (order_number, order_line_number, product_key, customer_key, order_date_key, ship_date_key,
     quantity, unit_price, product_cost, sales_amount)
SELECT
    s.order_number,
    s.order_line_number::SMALLINT,
    p.product_key,
    c.customer_key,
    s.orderdatekey::INTEGER,
    s.shipdatekey::INTEGER,
    s.quantity::INTEGER,
    s.unit_price::NUMERIC,
    s.product_cost::NUMERIC,
    s.sales_amount::NUMERIC
FROM dw_ventas.stg_ventas s
JOIN dw_ventas.dim_product  p ON p.product_id  = s.productkey::INTEGER
JOIN dw_ventas.dim_customer c ON c.customer_id = s.customerkey::INTEGER
ORDER BY s.order_number;

SELECT 'dim_product'  AS tabla, COUNT(*) AS filas FROM dw_ventas.dim_product
UNION ALL SELECT 'dim_customer', COUNT(*) FROM dw_ventas.dim_customer
UNION ALL SELECT 'dim_date',     COUNT(*) FROM dw_ventas.dim_date
UNION ALL SELECT 'fact_sales',   COUNT(*) FROM dw_ventas.fact_sales;

SELECT (SELECT COUNT(*) FROM dw_ventas.stg_ventas)             AS filas_staging,
       (SELECT COUNT(*) FROM dw_ventas.fact_sales)             AS filas_hechos,
       (SELECT SUM(sales_amount::NUMERIC) FROM dw_ventas.stg_ventas) AS ventas_staging,
       (SELECT SUM(sales_amount) FROM dw_ventas.fact_sales)    AS ventas_hechos,
       (SELECT SUM(quantity::INTEGER) FROM dw_ventas.stg_ventas)     AS unidades_staging,
       (SELECT SUM(quantity) FROM dw_ventas.fact_sales)        AS unidades_hechos;
