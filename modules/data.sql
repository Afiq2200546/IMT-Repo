-- ====================================================
-- Use the database (assumes it already exists)
-- ====================================================
USE `imt-database`;

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
INSERT INTO Products (name, quantity, price, category_id, user_id, alarm_stock_level, image_url) VALUES
    ('Laptop', 50, 1200.00, 1, 2, 10, 'https://m.media-amazon.com/images/I/61LdecwlWYL.jpg'),
    ('Smartphone', 200, 800.00, 1, 2, 20, 'https://images-cdn.ubuy.co.in/633fd9ec9f50f57b704f1be2-hilitand-s22-ultra-unlocked-smartphone.jpg'),
    ('Jeans', 150, 40.00, 2, 2, 15, 'https://shop.mango.com/assets/rcs/pics/static/T7/fotos/S/77034443_TM_B.jpg'),
    ('T-Shirt', 300, 20.00, 2, 5, 30, 'https://contents.mediadecathlon.com/p2606947/k$1c9e0ffdefc3e67bdeabc82be7893e93/men-s-running-quick-dry-t-shirt-red-decathlon-8771124.jpg'),
    ('Garden Chair', 75, 150.00, 3, 5, 10, 'https://i.ebayimg.com/images/g/8FAAAOSwSqBl4DKZ/s-l400.jpg'),
    ('Table Lamp', 80, 70.00, 3, 5, 15, 'https://www.islandliving.sg/cdn/shop/products/small_stone_table_lamp_2.jpg');
