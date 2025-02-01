import mysql.connector
from mysql.connector import Error

class DatabaseCRUD:
    def __init__(self, host, user, password, database):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            print("Connected to database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

    # Company CRUD Operations
    def create_company(self, name, email):
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO Company (name, email) VALUES (%s, %s)"
            cursor.execute(query, (name, email))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error creating company: {e}")
            self.connection.rollback()
            return None

    def get_all_companies(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Company")
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting companies: {e}")
            return None

    def update_company(self, company_id, name=None, email=None):
        try:
            cursor = self.connection.cursor()
            updates = []
            params = []

            if name:
                updates.append("name = %s")
                params.append(name)
            if email:
                updates.append("email = %s")
                params.append(email)

            params.append(company_id)
            query = f"UPDATE Company SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount
        except Error as e:
            print(f"Error updating company: {e}")
            self.connection.rollback()
            return None

    def delete_company(self, company_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Company WHERE id = %s", (company_id,))
            self.connection.commit()
            return cursor.rowcount
        except Error as e:
            print(f"Error deleting company: {e}")
            self.connection.rollback()
            return None

    # Users CRUD Operations
    def create_user(self, username, password, role, email, company_id=None):
        try:
            cursor = self.connection.cursor()
            query = """INSERT INTO Users 
                    (username, password, role, email, company_id)
                    VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (username, password, role, email, company_id))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error creating user: {e}")
            self.connection.rollback()
            return None

    def get_user(self, user_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Users WHERE id = %s", (user_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error getting user: {e}")
            return None

    # Add similar CRUD methods for Category and Products
    # Category CRUD Operations
    def create_category(self, name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO Category (name) VALUES (%s)", (name,))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error creating category: {e}")
            self.connection.rollback()
            return None

    # Products CRUD Operations
    def create_product(self, name, quantity, price, category_id, alarm_stock_level):
        try:
            cursor = self.connection.cursor()
            query = """INSERT INTO Products 
                    (name, quantity, price, category_id, alarm_stock_level)
                    VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (name, quantity, price, category_id, alarm_stock_level))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error creating product: {e}")
            self.connection.rollback()
            return None

    def get_products_by_category(self, category_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Products WHERE category_id = %s", (category_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting products: {e}")
            return None
