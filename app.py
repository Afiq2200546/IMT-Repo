import pymongo
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    g,
    jsonify,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import base64

from dotenv import load_dotenv
import os

from modules.aws_db import DatabaseCRUD

load_dotenv()

aws_db = DatabaseCRUD(
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DB')
)

# Create a Flask app and set a secret key
app = Flask(__name__)
app.app_context().push()
app.config["SECRET_KEY"] = "your_secret_key_here"

# Define teardown app context
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


# Define x route
@app.route("/")
def home():
    if not session.get("accountId"):
        return redirect(url_for("login"))

    aws_db.connect()
    user = aws_db.get_user(session["accountId"])

    if user["role"] == "Admin":
        # Get all users from the same company for admin dashboard
        company_users = aws_db.get_users_by_company(user["company_id"])
        aws_db.disconnect()
        return render_template("admin_dashboard.html", users=company_users)
    else:
        # Regular product listing for Staff and Manager
        products = aws_db.get_products_by_company_id(user["company_id"])
        categories = aws_db.get_categories()
        aws_db.disconnect()
        return render_template("index.html", products=products, categories=categories, role=user["role"])
    # if "accountId" in session and "accountRole" in session:
    #     id = session["accountId"]
    #     role = session["accountRole"]
    #
    #     if role == "filmmaker":
    #         return redirect(url_for("filmmaker.dashboard"))
    #
    # try:
    #     # Connect to the database
    #     db = get_sqlite_database()
    #     cursor = db.cursor()
    #
    #     # Display all films from the database
    #     cursor.execute(
    #         "SELECT DISTINCT Film.filmId, Film.filmName, Film.filmRunTime, Film.filmPoster FROM Film JOIN Screening ON Film.filmId = Screening.filmId WHERE Screening.screeningStatus != 'Finished'"
    #     )
    #     films_data = cursor.fetchall()
    #     films_list = []
    #
    #     for film_data in films_data:
    #         film_id, film_name, film_runtime, film_poster_blob = film_data
    #
    #         # Convert Blob to Base64 String
    #         film_poster_base64 = base64.b64encode(film_poster_blob).decode("utf-8")
    #
    #         film_info = {
    #             "film_id": film_id,
    #             "film_name": film_name,
    #             "film_runtime": film_runtime,
    #             "film_poster_base64": film_poster_base64,
    #         }
    #         films_list.append(film_info)
    #
    #     return render_template("index.html", films_list=films_list)
    #
    # except Exception as e:
    #     db.rollback()
    #     print(f"An error occurred: {e}")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "accountId" in session:
        user_id = session["accountId"]
        aws_db.connect()
        
        if request.method == "POST":
            updated_username = request.form.get("username")
            updated_email = request.form.get("email")
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")

            user = aws_db.get_user(user_id)

            # If password change is requested
            if current_password and new_password and confirm_password:
                # Check if current password is correct
                #if not check_password_hash(user["password"], current_password):
                if not user["password"]:
                    flash("Current password is incorrect.", "danger")
                    return redirect(url_for("profile"))

                # Check if new passwords match
                if new_password != confirm_password:
                    flash("New passwords do not match.", "danger")
                    return redirect(url_for("profile"))

                # Update password
                #password_hash = generate_password_hash(new_password_
                aws_db.update_user(user_id, password=new_password)
                flash("Password updated successfully!", "success")

            # Update other user information
            aws_db.update_user(user_id, username=updated_username, email=updated_email)
            flash("Your profile has been updated!", "success")
            return redirect(url_for("profile"))
        
        user = aws_db.get_user(user_id)
        company = aws_db.get_company(user["company_id"]) if user["company_id"] else None
        aws_db.disconnect()
        
        return render_template("profilepage.html", user=user, company=company)
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Please provide both email and password", "danger")
            return render_template("login.html", error=True)

        try:
            aws_db.connect()
            user = aws_db.get_user_by_email(email)
            aws_db.disconnect()

            if not user:
                flash("Email not found. Please check your email or register.", "danger")
                return render_template("login.html", error=True)
            
            #if not check_password_hash(user["password"], password): #Uncomment this line if using hashed passwords
            if user["password"] != password:  #Remove this line when using hashed passwords
                flash("Invalid password. Please try again.", "danger")
                return render_template("login.html", error=True)

            # Login successful
            session["accountId"] = user["id"]
            session["accountRole"] = user["role"]
            flash("Login successful!", "success")
            return redirect(url_for("home"))

        except Exception as e:
            flash(f"An error occurred while logging in. Please try again.", "danger")
            return render_template("login.html", error=True)

    return render_template("login.html")


# Define account logout route
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# Define account registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get company information
        company_name = request.form.get("company_name")
        company_email = request.form.get("company_email")
        
        # Get admin account information
        username = request.form.get("username")
        email = request.form.get("email")
        password_hash = generate_password_hash(request.form.get("password"))

        aws_db.connect()
        
        try:
            # Create new company
            company_id = aws_db.create_company(company_name, company_email)
            
            if company_id:
                # Create admin user associated with the company
                user_id = aws_db.create_user(
                    username=username,
                    password=password_hash,
                    role="Admin",
                    email=email,
                    company_id=company_id
                )
                
                if user_id:
                    aws_db.disconnect()
                    flash("Company and admin account created successfully!", "success")
                    return redirect(url_for("login"))
                else:
                    # If user creation fails, delete the company
                    aws_db.delete_company(company_id)
                    raise Exception("Failed to create admin user")
            else:
                raise Exception("Failed to create company")
                
        except Exception as e:
            aws_db.disconnect()
            flash(f"Registration failed: {str(e)}", "error")
            return redirect(url_for("register"))

    return render_template("register.html")

# Combine both routes into one
@app.route("/product/<int:product_id>", methods=["GET", "POST"])
@app.route("/product/new", methods=["GET", "POST"])
def manage_product(product_id=None):
    if not session.get("accountId"):
        return redirect(url_for("login"))
    
    aws_db.connect()
    user = aws_db.get_user(session["accountId"])
    
    # For creating new product, only Manager can access
    if product_id is None and user["role"] != "Manager":
        flash("Only Managers can create new products.", "danger")
        return redirect(url_for("home"))
    
    # For editing, Admin cannot access
    if product_id is not None and user["role"] == "Admin":
        flash("Admins don't have permission to edit products.", "danger")
        return redirect(url_for("home"))
    
    # Get existing product if editing
    product = aws_db.get_product(product_id) if product_id else None
    is_update = product is not None

    if request.method == "POST":
        name = request.form.get("name")
        quantity = request.form.get("quantity")
        price = request.form.get("price")
        category_id = request.form.get("category_id")
        alarm_stock_level = request.form.get("alarm_stock_level")
        image_url = request.form.get("image_url")
        
        try:
            if is_update:
                aws_db.update_product(
                    product_id,
                    name=name,
                    quantity=int(quantity),
                    price=float(price),
                    category_id=int(category_id),
                    alarm_stock_level=int(alarm_stock_level),
                    image_url=image_url
                )
                flash("Product updated successfully!", "success")
            else:
                aws_db.create_product(
                    name=name,
                    quantity=int(quantity),
                    price=float(price),
                    category_id=int(category_id),
                    user_id=user["id"],
                    alarm_stock_level=int(alarm_stock_level),
                    image_url=image_url
                )
                flash("Product created successfully!", "success")
            return redirect(url_for("home"))
        except Exception as e:
            flash(f"Error {'updating' if is_update else 'creating'} product: {str(e)}", "danger")
    
    categories = aws_db.get_categories()
    aws_db.disconnect()
        
    return render_template(
        "manage_product.html",
        product=product,
        categories=categories,
        is_update=is_update
    )
@app.route("/product/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    if not session.get("accountId"):
        return redirect(url_for("login"))
    
    aws_db.connect()
    user = aws_db.get_user(session["accountId"])
    
    # Check if user has permission (Manager or Staff)
    if user["role"] == "Admin":
        flash("Admins don't have permission to delete products.", "danger")
        return redirect(url_for("home"))
    
    try:
        aws_db.delete_product(product_id)
        flash("Product deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting product: {str(e)}", "danger")
    
    aws_db.disconnect()
    return redirect(url_for("home"))

@app.route("/user/<int:user_id>", methods=["GET", "POST"])
@app.route("/user/new", methods=["GET", "POST"])
def manage_user(user_id=None):
    if not session.get("accountId"):
        return redirect(url_for("login"))
    
    aws_db.connect()
    admin = aws_db.get_user(session["accountId"])
    
    # Only Admin can access
    if admin["role"] != "Admin":
        flash("Only administrators can access this page.", "danger")
        return redirect(url_for("home"))
    
    # Get existing user if editing
    user = aws_db.get_user(user_id) if user_id else None
    is_update = user is not None

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        role = request.form.get("role")
        password = request.form.get("password")
        
        try:
            if is_update:
                # Don't update password if not provided
                if password:
                    password_hash = generate_password_hash(password)
                    aws_db.update_user(user_id, username=username, email=email, role=role, password=password_hash)
                else:
                    aws_db.update_user(user_id, username=username, email=email, role=role)
                flash("User updated successfully!", "success")
            else:
                password_hash = generate_password_hash(password)
                aws_db.create_user(
                    username=username,
                    password=password_hash,
                    role=role,
                    email=email,
                    company_id=admin["company_id"]
                )
                flash("User created successfully!", "success")
            return redirect(url_for("home"))
        except Exception as e:
            flash(f"Error {'updating' if is_update else 'creating'} user: {str(e)}", "danger")
    
    aws_db.disconnect()
    return render_template("manage_user.html", user=user, is_update=is_update)

@app.route("/user/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if not session.get("accountId"):
        return redirect(url_for("login"))
    
    aws_db.connect()
    admin = aws_db.get_user(session["accountId"])
    
    # Only Admin can delete users
    if admin["role"] != "Admin":
        flash("Only administrators can delete users.", "danger")
        return redirect(url_for("home"))
    
    # Cannot delete self
    if user_id == admin["id"]:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("home"))
    
    try:
        target_user = aws_db.get_user(user_id)
        # Can only delete users from same company
        if target_user["company_id"] != admin["company_id"]:
            flash("You can only delete users from your own company.", "danger")
            return redirect(url_for("home"))
        
        aws_db.delete_user(user_id)
        flash("User deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting user: {str(e)}", "danger")
    
    aws_db.disconnect()
    return redirect(url_for("home"))

# Define error 404 route
@app.route("/error")
def error404():
    return render_template("error404.html")


if __name__ == "__main__":
    #app.run(debug=True)
     app.run(host='0.0.0.0', port=5000, debug=True)
