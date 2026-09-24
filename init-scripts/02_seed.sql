SET search_path TO shop;

INSERT INTO categories (name) VALUES
    ('Electronics'),
    ('Books'),
    ('Home & Kitchen'),
    ('Sports & Outdoors');

INSERT INTO customers (first_name, last_name, email, country) VALUES
    ('Ava',   'Nguyen',   'ava.nguyen@example.com',   'USA'),
    ('Liam',  'Smith',    'liam.smith@example.com',   'UK'),
    ('Sofia', 'Rossi',    'sofia.rossi@example.com',  'Italy'),
    ('Noah',  'Müller',   'noah.mueller@example.com', 'Germany'),
    ('Mia',   'Tanaka',   'mia.tanaka@example.com',   'Japan');

INSERT INTO products (name, category_id, price, stock_quantity) VALUES
    ('Wireless Mouse',        1, 19.99, 150),
    ('Mechanical Keyboard',   1, 79.99, 80),
    ('Noise-Cancelling Headphones', 1, 149.99, 40),
    ('The Pragmatic Programmer', 2, 34.50, 60),
    ('Clean Code',            2, 29.95, 55),
    ('Stainless Steel Pan',   3, 45.00, 30),
    ('Coffee Maker',          3, 65.00, 25),
    ('Yoga Mat',              4, 22.00, 100),
    ('Running Shoes',         4, 89.99, 70);

INSERT INTO orders (customer_id, status) VALUES
    (1, 'delivered'),
    (2, 'shipped'),
    (3, 'paid'),
    (1, 'pending'),
    (4, 'delivered'),
    (5, 'cancelled');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 2, 19.99),
    (1, 4, 1, 34.50),
    (2, 3, 1, 149.99),
    (3, 8, 3, 22.00),
    (4, 2, 1, 79.99),
    (5, 5, 2, 29.95),
    (5, 9, 1, 89.99),
    (6, 6, 1, 45.00);
