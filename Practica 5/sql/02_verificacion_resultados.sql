SELECT 'raw_sales' AS tabla, COUNT(*) AS filas FROM raw_sales
UNION ALL SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL SELECT 'dim_date', COUNT(*) FROM dim_date
UNION ALL SELECT 'fact_sales', COUNT(*) FROM fact_sales;

SELECT COUNT(DISTINCT product_id) AS productos,
       COUNT(DISTINCT (product_id, category, subcategory)) AS combinaciones_producto_categoria,
       COUNT(DISTINCT customer_id) AS clientes,
       COUNT(DISTINCT order_date) AS fechas
FROM raw_sales;

SELECT * FROM dim_product
WHERE product_id = 'P186'
ORDER BY product_key;

SELECT (SELECT COUNT(*) FROM fact_sales
        WHERE product_key IS NULL OR customer_key IS NULL
           OR date_key IS NULL)                  AS hechos_sin_clave,
       (SELECT SUM(sales_amount) FROM raw_sales)  AS ventas_staging,
       (SELECT SUM(sales_amount) FROM fact_sales) AS ventas_hechos,
       (SELECT SUM(quantity) FROM raw_sales)      AS unidades_staging,
       (SELECT SUM(quantity) FROM fact_sales)     AS unidades_hechos;

SELECT r.category, r.ventas_staging, h.ventas_hechos,
       r.ventas_staging - h.ventas_hechos AS diferencia
FROM (SELECT category, SUM(sales_amount) AS ventas_staging
      FROM raw_sales GROUP BY category) r
JOIN (SELECT d.category, SUM(f.sales_amount) AS ventas_hechos
      FROM fact_sales f
      JOIN dim_product d ON f.product_key = d.product_key
      GROUP BY d.category) h ON h.category = r.category
ORDER BY r.category;

SELECT * FROM fact_sales LIMIT 10;

SELECT d.category, dt.month, SUM(f.sales_amount) as total
FROM fact_sales f
JOIN dim_product d ON f.product_key = d.product_key
JOIN dim_date dt ON f.date_key = dt.date_key
GROUP BY d.category, dt.month;

SELECT dt.year, dt.month, d.category,
       COUNT(*)            AS numero_ventas,
       SUM(f.sales_amount) AS total_vendido
FROM fact_sales f
JOIN dim_product d ON f.product_key = d.product_key
JOIN dim_date dt ON f.date_key = dt.date_key
GROUP BY dt.year, dt.month, d.category
ORDER BY dt.year, dt.month, d.category;

SELECT c.customer_id, c.customer_name, c.gender,
       SUM(f.sales_amount) AS total_vendido
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_id, c.customer_name, c.gender
ORDER BY total_vendido DESC;

SELECT c.gender,
       COUNT(DISTINCT c.customer_id) AS clientes,
       COUNT(*)                      AS numero_ventas,
       SUM(f.sales_amount)           AS total_vendido
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.gender
ORDER BY c.gender;
