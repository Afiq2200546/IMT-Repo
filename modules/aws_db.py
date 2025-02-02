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
    
    def get_company(self, company_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Company WHERE id = %s", (company_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error getting company: {e}")
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
    
    def get_user_by_email(self, email):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching user: {e}")
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
    def create_product(self, name, quantity, price, category_id, user_id, alarm_stock_level, image_url):
        try:
            cursor = self.connection.cursor()
            query = """INSERT INTO Products 
                    (name, quantity, price, category_id, user_id, alarm_stock_level, image_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (name, quantity, price, category_id, user_id, alarm_stock_level, image_url))
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

    def get_products_by_company_id(self, company_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT Products.* FROM Products, Users, Company "
                           "WHERE Company.id = %s "
                           "AND Users.company_id = Company.id "
                           "AND Products.user_id = Users.id", (company_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting products: {e}")
            return None

    def get_all_products(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Products")
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting products: {e}")
            return None

    def update_product(self, product_id, name=None, quantity=None, price=None, category_id=None, user_id=None, alarm_stock_level=None,
                       image_url=None):
        try:
            cursor = self.connection.cursor()
            updates = []
            params = []

            if name:
                updates.append("name = %s")
                params.append(name)
            if quantity is not None:
                updates.append("quantity = %s")
                params.append(quantity)
            if price is not None:
                updates.append("price = %s")
                params.append(price)
            if category_id is not None:
                updates.append("category_id = %s")
                params.append(category_id)
            if user_id is not None:
                updates.append("user_id = %s")
                params.append(user_id)
            if alarm_stock_level is not None:
                updates.append("alarm_stock_level = %s")
                params.append(alarm_stock_level)
            if image_url:
                updates.append("image_url = %s")
                params.append(image_url)

            params.append(product_id)
            query = f"UPDATE Products SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount
        except Error as e:
            print(f"Error updating product: {e}")
            self.connection.rollback()
            return None

    def update_user(self, user_id, username=None, password=None, role=None, email=None, company_id=None):
        try:
            cursor = self.connection.cursor()
            updates = []
            params = []

            if username:
                updates.append("username = %s")
                params.append(username)
            if password:
                updates.append("password = %s")
                params.append(password)
            if role:
                updates.append("role = %s")
                params.append(role)
            if email:
                updates.append("email = %s")
                params.append(email)
            if company_id is not None:
                updates.append("company_id = %s")
                params.append(company_id)

            params.append(user_id)
            query = f"UPDATE Users SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount
        except Error as e:
            print(f"Error updating user: {e}")
            self.connection.rollback()
            return None

    def update_category(self, category_id, name=None):
        try:
            cursor = self.connection.cursor()
            updates = []
            params = []

            if name:
                updates.append("name = %s")
                params.append(name)

            params.append(category_id)
            query = f"UPDATE Category SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount
        except Error as e:
            print(f"Error updating category: {e}")
            self.connection.rollback()
            return None

    def get_categories(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Category")
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting products: {e}")
            return None
