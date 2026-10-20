SELECT d.year, d.month, d.month_name, p.category,
       COUNT(DISTINCT f.order_number) AS total_ventas,
       SUM(f.sales_amount)            AS ingreso_total
FROM dw_ventas.fact_sales f
JOIN dw_ventas.dim_product p ON p.product_key = f.product_key
JOIN dw_ventas.dim_date    d ON d.date_key    = f.order_date_key
GROUP BY d.year, d.month, d.month_name, p.category
ORDER BY d.year, d.month, p.category;

SELECT d.month, d.month_name, p.category,
       COUNT(DISTINCT f.order_number) AS total_ventas,
       SUM(f.sales_amount)            AS ingreso_total
FROM dw_ventas.fact_sales f
JOIN dw_ventas.dim_product p ON p.product_key = f.product_key
JOIN dw_ventas.dim_date    d ON d.date_key    = f.order_date_key
GROUP BY d.month, d.month_name, p.category
ORDER BY d.month, p.category;

SELECT c.customer_id, c.gender,
       SUM(f.sales_amount) AS ingreso_total
FROM dw_ventas.fact_sales f
JOIN dw_ventas.dim_customer c ON c.customer_key = f.customer_key
GROUP BY c.customer_id, c.gender
ORDER BY ingreso_total DESC;

SELECT p.product_id, p.product_name,
       SUM(f.quantity) AS cantidad_total
FROM dw_ventas.fact_sales f
JOIN dw_ventas.dim_product p ON p.product_key = f.product_key
GROUP BY p.product_id, p.product_name
ORDER BY cantidad_total DESC, p.product_id;

SELECT d.year, d.month, d.month_name,
       SUM(f.quantity) AS cantidad_enviada
FROM dw_ventas.fact_sales f
JOIN dw_ventas.dim_date d ON d.date_key = f.ship_date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

SELECT d.month, d.month_name,
       SUM(f.quantity) AS cantidad_enviada
FROM dw_ventas.fact_sales f
JOIN dw_ventas.dim_date d ON d.date_key = f.ship_date_key
GROUP BY d.month, d.month_name
ORDER BY d.month;

SELECT p.size, c.marital_status,
       SUM(f.sales_amount) AS ventas_total,
       SUM(f.quantity)     AS unidades
FROM dw_ventas.fact_sales f
JOIN dw_ventas.dim_product  p ON p.product_key  = f.product_key
JOIN dw_ventas.dim_customer c ON c.customer_key = f.customer_key
GROUP BY p.size, c.marital_status
ORDER BY CASE p.size WHEN 'Small' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, c.marital_status;
