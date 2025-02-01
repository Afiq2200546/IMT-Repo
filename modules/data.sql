-- ====================================================
-- Use the database (assumes it already exists)
-- ====================================================
USE `database-1`;

-- ====================================================
-- Insert data into the Company table
-- ====================================================
INSERT INTO Company (name, email) VALUES
    ('TechCorp', 'info@techcorp.com'),
    ('Retail Inc', 'contact@retailinc.com');

-- ====================================================
-- Insert data into the Users table
-- (User authentication with role-based access: Admin, Manager, Staff)
-- ====================================================
-- For the purpose of this example, the password field contains placeholder text.
-- In a production environment, be sure to store a securely hashed password.
INSERT INTO Users (username, password, role, email, company_id) VALUES
    ('admin1', 'passwordhash1', 'Admin', 'admin1@techcorp.com', 1),
    ('manager1', 'passwordhash2', 'Manager', 'manager1@techcorp.com', 1),
    ('staff1', 'passwordhash3', 'Staff', 'staff1@techcorp.com', 1),
    ('admin2', 'passwordhash4', 'Admin', 'admin2@retailinc.com', 2),
    ('manager2', 'passwordhash5', 'Manager', 'manager2@retailinc.com', 2),
    ('staff2', 'passwordhash6', 'Staff', 'staff2@retailinc.com', 2);

-- ====================================================
-- Insert data into the Category table
-- (Product categories)
-- ====================================================
INSERT INTO Category (name) VALUES
    ('Electronics'),
    ('Clothing'),
    ('Home & Garden');

-- ====================================================
-- Insert data into the Products table
-- (Inventory tracking: add, remove, update stock levels)
-- ====================================================
INSERT INTO Products (name, quantity, price, category_id, alarm_stock_level) VALUES
    ('Laptop', 50, 1200.00, 1, 10),
    ('Smartphone', 200, 800.00, 1, 20),
    ('Jeans', 150, 40.00, 2, 15),
    ('T-Shirt', 300, 20.00, 2, 30),
    ('Garden Chair', 75, 150.00, 3, 10),
    ('Table Lamp', 80, 70.00, 3, 15);
