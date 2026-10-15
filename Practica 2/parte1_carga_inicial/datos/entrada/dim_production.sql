CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.dim_production (
    product_id VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50)
);

INSERT INTO staging.dim_production (product_id, product_name, category, subcategory)
VALUES
  ('P001', 'Notebook Classic', 'Office Supplies', 'Notebooks'),
  ('P002', 'Ballpoint Pen', 'Office Supplies', 'Writing'),
  ('P003', 'LED Monitor 24"', 'Technology', 'Monitors'),
  ('P004', 'Wireless Mouse', 'Technology', 'Accessories'),
  ('P005', 'Water Bottle 1L', 'Fitness', 'Hydration'),
  ('P006', 'Yoga Mat', 'Fitness', 'Mats'),
  ('P007', 'Desk Chair', 'Furniture', 'Chairs'),
  ('P008', 'Standing Desk', 'Furniture', 'Desks'),
  ('P009', 'Smartphone Stand', 'Technology', 'Accessories'),
  ('P010', 'Highlighter Set', 'Office Supplies', 'Writing');
