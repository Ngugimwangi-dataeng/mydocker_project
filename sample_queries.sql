SET search_path TO shop;

-- 1. Total revenue per customer
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    SUM(oi.quantity * oi.unit_price) AS total_spent
FROM customers c
JOIN orders o       ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id  = o.order_id
GROUP BY c.customer_id, customer_name
ORDER BY total_spent DESC;

-- 2. Best-selling products by quantity
SELECT
    p.name,
    SUM(oi.quantity) AS units_sold
FROM products p
JOIN order_items oi ON oi.product_id = p.product_id
GROUP BY p.name
ORDER BY units_sold DESC;

-- 3. Revenue by category
SELECT
    cat.name AS category,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM categories cat
JOIN products p      ON p.category_id = cat.category_id
JOIN order_items oi  ON oi.product_id = p.product_id
GROUP BY cat.name
ORDER BY revenue DESC;

-- 4. Orders with status and item count
SELECT
    o.order_id,
    o.status,
    o.order_date,
    COUNT(oi.order_item_id) AS item_count
FROM orders o
LEFT JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.order_id, o.status, o.order_date
ORDER BY o.order_date;

-- 5. Products low on stock (below 50 units)
SELECT name, stock_quantity
FROM products
WHERE stock_quantity < 50
ORDER BY stock_quantity ASC;

-- 6. Running total of revenue over time (window function)
SELECT
    o.order_date::date AS order_day,
    SUM(oi.quantity * oi.unit_price) AS daily_revenue,
    SUM(SUM(oi.quantity * oi.unit_price)) OVER (ORDER BY o.order_date::date) AS running_total
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY order_day
ORDER BY order_day;
