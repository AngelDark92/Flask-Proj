from flask import Flask, render_template, make_response, url_for, jsonify, redirect, session, flash, request
from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp
from datetime import datetime
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

# Some code coming from CS50 Finance assignement

# Configure flask and sqlite
app = Flask(__name__)
db = SQL("sqlite:///tavernetta.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["TEMPLATES_AUTO_RELOAD"] = True

# definition of value in £
def pound(value):
    """Format value as Pound."""
    return f"£ {value:,.2f}"

# importing definition in jinja
app.jinja_env.filters["pound"] = pound

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/login/", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return flash("Must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return flash("Must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return flash("Invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect(url_for("index"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout/")
@login_required
def logout():

    session.clear()
    flash("You have been logged out!")
    # Redirect to the homepage
    return redirect (url_for("index"))


@app.route("/check/", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    if request.method == "GET":

        result = db.execute("SELECT username FROM users WHERE username = :name",
                            name=request.args.get("username"))
        # check if username already exists
        if not result:
            return jsonify(True)
        else:
            return jsonify(False)

    # in case of post to check
    else:
        return flash("This page does not do anything.")


@app.route("/register/", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        name = request.form.get("username")

        # getting both passwords to check again if they are equal
        password = request.form.get("password")
        passw2 = request.form.get("confirmation")

        # checking wether the fields are left blank
        if password == "" or passw2 == "" or name == "":
            return flash("Missing username or passwords!")
        elif not password == passw2:
            return flash("Passwords do not match")

        # password protection with hash using the sha256 algorithm
        hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        insert = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hashed)",
                            username=request.form.get("username"), hashed=hashed)

        # check if insert has worked, if not username was already taken
        if not insert:
            return flash("Username already taken")

        # log the user in automatically as per /login/
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=name)
        session["user_id"] = rows[0]["id"]
        return redirect(url_for("index"))

    # if the request is get renders template register.html
    else:
        return render_template("register.html")


@app.route("/admin_orders/", methods=["GET", "POST"])
@login_required
def admin_orders():
    if session["user_id"] == 1:
        if request.method == "GET":
            return render_template("admin_orders.html")
    else:
        return redirect(url_for("index"))


@app.route("/clear_orders/", methods=["GET", "POST"])
@login_required
def clear_orders():
    if session["user_id"] == 1:
        if request.method == "GET":
            return render_template("admin_orders.html")
    else:
        return redirect(url_for("index"))

@app.route("/passw/", methods=["GET", "POST"])
@login_required
def passw():
    """Allows the user to change password"""

    if request.method == "POST":

        # check if all passwords are entered if javascript fails
        if not request.form.get("old_pw") or not request.form.get("password1") or not request.form.get("password2"):
            return flash("All fields must be filled out.")

        # get the passwords
        old_pw = request.form.get("old_pw")
        passw1 = request.form.get("password1")
        passw2 = request.form.get("password2")

        # check if password is same as before
        if old_pw == passw1:
            return flash("The new password needs to be different from the old one.")

        # get the row for current userid
        rows = db.execute("SELECT hash FROM users WHERE id = :userid", userid=session["user_id"])

        # check if old_pw is correct with the hash of the current userid
        if not check_password_hash(rows[0]["hash"], old_pw):
            return flash("Password entered does not match with your current one.")

        # check if passwords are the same
        if passw1 != passw2:
            return flash("New passwords do not match.")

        # update password for userid and flash message. updating with passw gives error for some reason
        new_hash = generate_password_hash(request.form.get("password1"), method='pbkdf2:sha256', salt_length=8)

        db.execute("UPDATE users SET hash = :new_hash WHERE id = :userid", userid=session["user_id"], new_hash=new_hash)
        flash("Password was changed!")

    return render_template("passw.html")


@app.route("/")
def index():
    # Todo
    return render_template ("index.html")


@app.route("/table/")
def table():
    # Todo
    return render_template ("table.html")


@app.route("/basket/")
@login_required
def basket():
    # Todo
    return render_template ("basket.html")


@app.route("/menu/")
def menu():
    # Todo
    return render_template ("menu.html")


@app.route("/orders/")
@login_required
def orders():
    # Todo
    return render_template ("orders.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return flash(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(debug = True)