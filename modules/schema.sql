-- ====================================================
-- Create the database (if it doesn't already exist)
-- ====================================================
CREATE DATABASE IF NOT EXISTS `imt-database`;
USE `imt-database`;

-- ====================================================
-- DROP EXISTING TABLES (if needed)
-- ====================================================
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Category;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Company;

-- ====================================================
-- TABLE: Company
-- ====================================================
CREATE TABLE Company (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    -- Additional fields (e.g., address, phone) can be added here
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ====================================================
-- TABLE: Users
-- (User authentication with role-based access: Admin, Manager, Staff)
-- ====================================================
CREATE TABLE Users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Manager', 'Staff') NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    company_id INT,
    -- Additional fields can be added here (e.g., first_name, last_name)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_company
        FOREIGN KEY (company_id)
        REFERENCES Company(id)
        ON DELETE SET NULL
);

-- ====================================================
-- TABLE: Category
-- (Product categories)
-- ====================================================
CREATE TABLE Category (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ====================================================
-- TABLE: Products
-- (Inventory tracking: add, remove, update stock levels)
-- ====================================================
CREATE TABLE Products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    category_id INT NOT NULL,
    user_id INT NOT NULL,
    alarm_stock_level INT NOT NULL,
    image_url VARCHAR(300) NOT NULL,
    -- Additional fields can be added here (e.g., description, supplier)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id)
        REFERENCES Category(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_products_user
        FOREIGN KEY (user_id)
        REFERENCES Users(id)
        ON DELETE CASCADE
);
