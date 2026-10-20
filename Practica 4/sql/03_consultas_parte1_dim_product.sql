SELECT category,
       COUNT(*) AS total_productos
FROM dim_product
GROUP BY category
ORDER BY total_productos DESC;

SELECT subcategory,
       COUNT(*) AS total_productos
FROM dim_product
GROUP BY subcategory
ORDER BY total_productos DESC;

SELECT product_id, product_name, subcategory
FROM dim_product
WHERE category = 'Beauty & Hygiene'
ORDER BY product_name;

SELECT product_id, product_name, category
FROM dim_product
WHERE subcategory = 'Biscuits & Cookies'
ORDER BY product_name;

SELECT category,
       COUNT(DISTINCT subcategory) AS total_subcategorias
FROM dim_product
GROUP BY category
ORDER BY total_subcategorias DESC, category;
