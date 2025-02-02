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
from modules.database import *
from blueprints.user import user
from blueprints.filmmaker import filmmaker, updateFilmScreeningStatus
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

# Register blueprints
app.register_blueprint(user, url_prefix="/user")
app.register_blueprint(filmmaker, url_prefix="/filmmaker")

# Define teardown app context
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


# Define home route
@app.route("/")
def home():
    aws_db.connect()

    products = aws_db.get_all_products()
    print(products)

    aws_db.disconnect()
    return render_template("index.html", products=products)
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


# Define profile route
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "accountId" in session:
        user_id = session["accountId"]
        aws_db.connect()
        
        if request.method == "POST":
            updated_username = request.form.get("username")
            updated_email = request.form.get("email")
            updated_phone_number = request.form.get("phonenumber")

            aws_db.update_user(user_id, username=updated_username, email=updated_email, phone_number=updated_phone_number)
            flash("Your account has been updated!", "success")
            return redirect(url_for("profile"))
        
        user = aws_db.get_user(user_id)
        company = aws_db.get_company(user["company_id"]) if user["company_id"] else None
        aws_db.disconnect()
        
        return render_template("profilepage.html", user=user, company=company)
    else:
        return redirect(url_for("login"))

@app.route("/moviebooking/<int:filmid>", methods=["GET", "POST"])
def moviebooking(filmid):
    try:
        # Connect to the database
        db = get_sqlite_database()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT Film.filmId, Film.filmmakerid, Film.filmName, Film.filmCast, 
            Film.filmPoster, Film.filmSynopsis, Film.filmRunTime, Film.filmReleaseDate,
            Film.filmMaturityRating,
                   COALESCE(Film.filmLanguage, "No information"), 
                   COALESCE(Film.filmGenre, "No information"), 
                   COALESCE(Filmmaker.filmmakerName, "No information")
            FROM Film 
            LEFT JOIN Filmmaker ON Film.filmmakerId = Filmmaker.filmmakerId 
            WHERE Film.filmId = ? 
        """,
            (filmid,),
        )
        data_row = cursor.fetchone()

        if not data_row:
            return redirect(url_for("error404"))

        film_data = data_row[:9]
        language, genre, filmmaker_name = data_row[9:]

        (
            film_id,
            _,
            film_name,
            film_cast,
            film_poster_blob,
            film_synopsis,
            film_runtime,
            film_release_date,
            film_maturity_rating,
        ) = film_data
        film_poster_base64 = base64.b64encode(film_poster_blob).decode("utf-8")

        updateFilmScreeningStatus(film_id, db, cursor)

        # Get the studios for this film
        cursor.execute(
            """
            SELECT DISTINCT Studio.studioId, Studio.studioName, Studio.studioAddress
            FROM Screening 
            JOIN Studio ON Screening.studioId = Studio.studioId 
            WHERE Screening.filmId = ? AND screeningStatus != "Finished"
        """,
            (filmid,),
        )
        studios = cursor.fetchall()

        # Get the film reviews with username from User table
        cursor.execute(
            """
            SELECT r.*, u.userName 
            FROM Film_Review r 
            INNER JOIN User u ON r.userId = u.userId 
            WHERE r.filmId = ?
        """,
            (filmid,),
        )

        reviews = cursor.fetchall()
        current_user_id = None
        if "accountId" in session:
            current_user_id = session["accountId"]

        userReview = False
        cursor.execute(
            """
            SELECT COUNT(*) FROM Booking
            WHERE userId = ? AND filmName = (
                SELECT filmName FROM Film WHERE filmId = ?
            )
            """,
            (current_user_id, filmid),
        )
        booking_count = cursor.fetchone()[0]
        userReview = booking_count > 0

        # Pass the reviews to the template
        return render_template(
            "moviebooking.html",
            filmid=film_id,
            film_name=film_name,
            film_cast=film_cast,
            film_poster_base64=film_poster_base64,
            film_synopsis=film_synopsis,
            film_runtime=film_runtime,
            film_release_date=film_release_date,
            film_maturity_rating=film_maturity_rating,
            studios=studios,
            reviews=reviews,
            film_language=language,
            film_genre=genre,
            filmmaker_name=filmmaker_name,
            current_user_id=current_user_id,
            userReview=userReview,
        )

    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")


@app.route("/get_screenings/<int:filmid>/<int:studioid>")
def get_screenings(filmid, studioid):
    try:
        db = get_sqlite_database()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT screeningDate, screeningTime, screeningCapacity, screeningOriginalCapacity, screeningId, screeningPrice
            FROM Screening
            WHERE filmId = ? AND studioId = ? AND screeningStatus != "Finished"
            ORDER BY screeningDate, screeningTime""",
            (filmid, studioid),
        )

        screenings = cursor.fetchall()

        result = {}
        for screening in screenings:
            date, time, capacity, originalCapacity, id, screeningPrice = screening

            if date not in result:
                result[date] = []

            result[date].append(
                {
                    "time": time,
                    "capacity": capacity,
                    "originalCapacity": originalCapacity,
                    "screeningId": id,
                    "screeningPrice": screeningPrice,
                }
            )
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"})


# Define account login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        aws_db.connect()
        user = aws_db.get_user_by_email(email)
        aws_db.disconnect()

        #if user and check_password_hash(user["password"], password):
        if user and user["password"] == password:
            session["accountId"] = user["id"]
            session["accountRole"] = user["role"]
            flash("You have successfully logged in.", "success")

            return redirect(url_for("home"))
        else:
            flash("Login failed. Please check your email and password.", "error")
            return redirect(url_for("login"))

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
        # Get the user input values from the input field
        username = request.form.get("username")
        email = request.form.get("email")
        password_hash = generate_password_hash(request.form.get("password"))
        phone_number = request.form.get("phonenumber")
        date_of_birth = request.form.get("dob")
        gender = request.form.get("gender")
        identity = request.form.get("identity")

        # Connect to the database
        db = get_sqlite_database()
        cursor = db.cursor()

        try:
            # Check if creation of the account is a user or filmmaker
            if identity == "user":
                cursor.execute(
                    "INSERT INTO User (userName, userEmail, userPassword, userPhoneNumber, userDOB, "
                    "userGender) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        username,
                        email,
                        password_hash,
                        phone_number,
                        date_of_birth,
                        gender,
                    ),
                )

            elif identity == "filmmaker":
                cursor.execute(
                    "INSERT INTO Filmmaker (filmmakerName, filmmakerEmail, filmmakerPassword, filmmakerPhoneNumber, filmmakerDOB, "
                    "filmmakerGender) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        username,
                        email,
                        password_hash,
                        phone_number,
                        date_of_birth,
                        gender,
                    ),
                )
            db.commit()
            flash("Your account has been created!", "success")
            return redirect(url_for("login"))

        except Exception as e:
            # Handle database errors and display an error message
            db.rollback()
            flash(
                "An error has occured during registration. Please try again later.",
                "error",
            )
            print("Error", e)
            return redirect(url_for("register"))

    else:
        return render_template("register.html")


# Define error 404 route
@app.route("/error")
def error404():
    return render_template("error404.html")


if __name__ == "__main__":
    # Initialise SQLite DB
    with app.app_context():
        create_all_tables(get_sqlite_database().cursor())

    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000, debug=True)
