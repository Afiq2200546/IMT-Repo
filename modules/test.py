#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

from modules.aws_db import DatabaseCRUD

load_dotenv()

if __name__ == "__main__":
    # Update these credentials with your MySQL information
    db = DatabaseCRUD(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DB')
    )

    try:
        db.connect()

        # # Example usage:
        # # Create a company
        # company_id = db.create_company("Tech Corp", "info@techcorp.com")
        # print(f"Created company with ID: {company_id}")
        #
        # # Create a user
        # user_id = db.create_user(
        #     username="admin1",
        #     password="secure123",
        #     role="Admin",
        #     email="admin@techcorp.com",
        #     company_id=company_id
        # )
        # print(f"Created user with ID: {user_id}")
        #
        # # Create a category
        # category_id = db.create_category("Electronics")
        # print(f"Created category with ID: {category_id}")
        #
        # # Create a product
        # product_id = db.create_product(
        #     name="Laptop",
        #     quantity=10,
        #     price=999.99,
        #     category_id=category_id,
        #     alarm_stock_level=5
        # )
        # print(f"Created product with ID: {product_id}")

        # Get all companies
        companies = db.get_all_companies()
        print("\nAll Companies:")
        for company in companies:
            print(f"{company['id']}: {company['name']} - {company['email']}")

    except Error as e:
        print(f"Database error: {e}")
    finally:
        db.disconnect()
