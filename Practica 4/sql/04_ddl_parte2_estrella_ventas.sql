CREATE SCHEMA IF NOT EXISTS dw_ventas;

DROP TABLE IF EXISTS dw_ventas.fact_sales;
DROP TABLE IF EXISTS dw_ventas.dim_product;
DROP TABLE IF EXISTS dw_ventas.dim_customer;
DROP TABLE IF EXISTS dw_ventas.dim_date;
DROP TABLE IF EXISTS dw_ventas.stg_ventas;

CREATE TABLE dw_ventas.stg_ventas (
    productkey         VARCHAR(20),
    product_code       VARCHAR(20),
    product_name       VARCHAR(150),
    list_price         VARCHAR(20),
    color              VARCHAR(30),
    size               VARCHAR(20),
    category           VARCHAR(80),
    subcategory        VARCHAR(80),
    customerkey        VARCHAR(20),
    birth_date         VARCHAR(20),
    marital_status     VARCHAR(20),
    gender             VARCHAR(5),
    income             VARCHAR(20),
    children           VARCHAR(10),
    home_owner         VARCHAR(5),
    cars               VARCHAR(10),
    orderdatekey       VARCHAR(10),
    order_date         VARCHAR(20),
    shipdatekey        VARCHAR(10),
    ship_date          VARCHAR(20),
    order_number       VARCHAR(20),
    order_line_number  VARCHAR(10),
    quantity           VARCHAR(10),
    unit_price         VARCHAR(20),
    product_cost       VARCHAR(20),
    sales_amount       VARCHAR(20)
);

CREATE TABLE dw_ventas.dim_product (
    product_key  BIGSERIAL PRIMARY KEY,
    product_id   INTEGER        NOT NULL UNIQUE,
    product_code VARCHAR(10)    NOT NULL UNIQUE,
    product_name VARCHAR(150)   NOT NULL,
    list_price   NUMERIC(10, 2) NOT NULL CHECK (list_price >= 0),
    color        VARCHAR(30)    NOT NULL,
    size         VARCHAR(20)    NOT NULL,
    category     VARCHAR(80)    NOT NULL,
    subcategory  VARCHAR(80)    NOT NULL
);

CREATE TABLE dw_ventas.dim_customer (
    customer_key   BIGSERIAL PRIMARY KEY,
    customer_id    INTEGER        NOT NULL UNIQUE,
    birth_date     DATE           NOT NULL,
    marital_status VARCHAR(10)    NOT NULL,
    gender         CHAR(1)        NOT NULL CHECK (gender IN ('M', 'F')),
    income         NUMERIC(12, 2) NOT NULL CHECK (income >= 0),
    children       SMALLINT       NOT NULL CHECK (children >= 0),
    home_owner     VARCHAR(3)     NOT NULL CHECK (home_owner IN ('Yes', 'No')),
    cars           SMALLINT       NOT NULL CHECK (cars >= 0)
);

CREATE TABLE dw_ventas.dim_date (
    date_key    INTEGER      PRIMARY KEY,
    full_date   DATE         NOT NULL UNIQUE,
    year        SMALLINT     NOT NULL,
    quarter     SMALLINT     NOT NULL,
    month       SMALLINT     NOT NULL,
    month_name  VARCHAR(12)  NOT NULL,
    year_month  CHAR(7)      NOT NULL,
    day         SMALLINT     NOT NULL,
    day_of_week SMALLINT     NOT NULL,
    day_name    VARCHAR(12)  NOT NULL,
    is_weekend  BOOLEAN      NOT NULL
);

CREATE TABLE dw_ventas.fact_sales (
    order_number      VARCHAR(10)    NOT NULL,
    order_line_number SMALLINT       NOT NULL,
    product_key       BIGINT         NOT NULL REFERENCES dw_ventas.dim_product (product_key),
    customer_key      BIGINT         NOT NULL REFERENCES dw_ventas.dim_customer (customer_key),
    order_date_key    INTEGER        NOT NULL REFERENCES dw_ventas.dim_date (date_key),
    ship_date_key     INTEGER        NOT NULL REFERENCES dw_ventas.dim_date (date_key),
    quantity          INTEGER        NOT NULL CHECK (quantity > 0),
    unit_price        NUMERIC(10, 2) NOT NULL,
    product_cost      NUMERIC(10, 2) NOT NULL,
    sales_amount      NUMERIC(12, 2) NOT NULL,
    PRIMARY KEY (order_number, order_line_number),
    CHECK (ship_date_key >= order_date_key)
);

CREATE INDEX ix_fact_sales_product    ON dw_ventas.fact_sales (product_key);
CREATE INDEX ix_fact_sales_customer   ON dw_ventas.fact_sales (customer_key);
CREATE INDEX ix_fact_sales_order_date ON dw_ventas.fact_sales (order_date_key);
CREATE INDEX ix_fact_sales_ship_date  ON dw_ventas.fact_sales (ship_date_key);

SELECT table_name, COUNT(*) AS columnas
FROM information_schema.columns
WHERE table_schema = 'dw_ventas'
GROUP BY table_name
ORDER BY table_name;
