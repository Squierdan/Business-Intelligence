DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS raw_sales;

CREATE TABLE raw_sales (
  product_id VARCHAR(10),
  product_name VARCHAR(100),
  category VARCHAR(50),
  subcategory VARCHAR(50),
  customer_id VARCHAR(10),
  customer_name VARCHAR(100),
  gender CHAR(1),
  marital_status VARCHAR(10),
  income INT,
  order_date DATE,
  quantity INT,
  unit_price NUMERIC(10,2),
  sales_amount NUMERIC(10,2)
);

CREATE TABLE dim_product (
  product_key SERIAL PRIMARY KEY,
  product_id VARCHAR(10),
  product_name VARCHAR(100),
  category VARCHAR(50),
  subcategory VARCHAR(50)
);

CREATE TABLE dim_customer (
  customer_key SERIAL PRIMARY KEY,
  customer_id VARCHAR(10),
  customer_name VARCHAR(100),
  gender CHAR(1),
  marital_status VARCHAR(10),
  income INT
);

CREATE TABLE dim_date (
  date_key DATE PRIMARY KEY,
  year INT,
  month INT,
  day INT,
  quarter VARCHAR(5)
);

CREATE TABLE fact_sales (
  transaction_key SERIAL PRIMARY KEY,
  product_key INT,
  customer_key INT,
  date_key DATE,
  quantity INT,
  unit_price NUMERIC(10,2),
  sales_amount NUMERIC(10,2)
);

SELECT table_name, COUNT(*) AS columnas
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN ('raw_sales', 'dim_product', 'dim_customer', 'dim_date', 'fact_sales')
GROUP BY table_name
ORDER BY table_name;
