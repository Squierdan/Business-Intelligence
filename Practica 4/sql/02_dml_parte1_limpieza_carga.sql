SELECT COUNT(*) AS total_registros
FROM stg_products;

SELECT COUNT(DISTINCT product_id) AS productos_unicos
FROM stg_products;

SELECT COUNT(DISTINCT category)    AS categorias,
       COUNT(DISTINCT subcategory) AS subcategorias
FROM stg_products;

SELECT COUNT(*) FILTER (WHERE product_name ~ E'\t')                      AS nombres_con_tabulacion,
       COUNT(*) FILTER (WHERE strpos(product_name, chr(160)) > 0)        AS nombres_con_espacio_no_separable,
       COUNT(*) FILTER (WHERE product_name ~ '\s{2,}')                   AS nombres_con_espacios_repetidos,
       COUNT(*) FILTER (WHERE product_name ~ '^\s|\s$')                  AS nombres_con_espacios_en_los_bordes
FROM stg_products;

UPDATE stg_products
SET product_name = btrim(regexp_replace(translate(product_name, chr(160), ' '), '\s+', ' ', 'g')),
    category     = btrim(category),
    subcategory  = btrim(subcategory);

SELECT COUNT(*) FILTER (WHERE product_name ~ E'\t')                      AS nombres_con_tabulacion,
       COUNT(*) FILTER (WHERE strpos(product_name, chr(160)) > 0)        AS nombres_con_espacio_no_separable,
       COUNT(*) FILTER (WHERE product_name ~ '\s{2,}')                   AS nombres_con_espacios_repetidos,
       COUNT(*) FILTER (WHERE product_name ~ '^\s|\s$')                  AS nombres_con_espacios_en_los_bordes
FROM stg_products;

SELECT product_id, COUNT(*)
FROM stg_products
GROUP BY product_id
HAVING COUNT(*) > 1;

SELECT *
FROM stg_products
WHERE product_id IS NULL OR product_id = '';

INSERT INTO dim_product
    (product_id, product_name, category, subcategory)
SELECT DISTINCT
    product_id,
    product_name,
    category,
    subcategory
FROM stg_products
ORDER BY product_id;

SELECT COUNT(*) AS total_dim_product FROM dim_product;

SELECT * FROM dim_product ORDER BY product_key LIMIT 20;
