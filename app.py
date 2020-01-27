from flask import Flask, render_template, make_response, url_for, jsonify, redirect, session, flash, request
from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp
from datetime import datetime
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import datetime

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
    return f"£{value:,.2f}"


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
    return redirect(url_for("index"))


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


@app.route("/menu/", methods=["GET", "POST"])
def menu():
    # be able to see menu and put items in basket
    if request.method == "POST":

        # check if entered data is int
        if session.get("user_id") and isinstance(int(request.form.get("num")), int):
            #retreive item name and print name and number of that item bought
            item_id = int(request.form.get("item"))
            num = int(request.form.get("num"))
            item = db.execute("SELECT name, available, price FROM items WHERE id = :item_id ", item_id=item_id)

            # final price for the number of items
            final_price = (int(item[0]["price"])) * num

            if int(item[0]["available"]) != 0:

                db.execute("INSERT INTO basket (item_id, user_id, total_price, item_name, number) VALUES(:item_id, :user_id, :total_price, :item_name, :number)",
                           item_id=item_id, user_id=session.get("user_id"), total_price=final_price, item_name=item[0]["name"], number=num)
                curr_num = db.execute("SELECT available FROM items WHERE id = :item_id", item_id=item_id)
                db.execute("UPDATE items SET available = :num_decrease WHERE id = :item_id", num_decrease=(int(curr_num[0]["available"]))-num, item_id=item_id)
                flash(f"{num} {item[0]['name']} added to your basket")

            else:
                flash(f"No {item[0]['name']}s available!")
                return redirect(url_for("menu"))
        else:
            flash(request.form.get("num"))
            flash("Can't do that!")

    items = db.execute("SELECT id, name, price, description, img FROM items WHERE id IN (0, 1, 2, 3, 4, 5) ORDER BY id")
    return render_template("menu.html", items=items)


@app.route("/", methods=["GET", "POST"])
def index():
    # main page of restaurant get number of items and add or remove them
    if request.method == "POST":
        if session.get("user_id") == 1:
            item_id = int(request.form.get("item"))
            num = int(request.form.get("num"))
            curr_num = db.execute("SELECT available, name FROM items WHERE id = :item_id", item_id=item_id)
            # final number for correct items
            num2 = (int(curr_num[0]["available"])) + num
            db.execute("UPDATE items SET available = :num2 WHERE id = :item_id", num2=num2, item_id=item_id)
            flash(f"{num} added to available {curr_num[0]['name']}s")
            return redirect(url_for("index"))
        else:
            flash("Can't do that!")
    items = db.execute("SELECT id, name, available, description, img FROM items WHERE id IN (0, 1, 2, 3, 4, 5) ORDER BY id")
    return render_template("index.html", items=items)


@app.route("/basket/", methods=["GET", "POST"])
@login_required
def basket():
    # be able to see basket, delete items if needed and buy them to be stored in orders
    # today's date to display and to check
    now = datetime.now()
    if request.method == "POST":
        # submit everything to orders and delete everything from basket
        # d1 from datetime.date gives yyyy-mm-dd
        d1 = datetime.date(now)
        # d2 from html gives back format yyyy-mm-dd
        d2_dirty = datetime.strptime(request.form.get("date"), '%Y-%m-%d')
        d2 = datetime.date(d2_dirty)
        if d2 >= d1:
            # first check if there are any items
            items2 = db.execute("SELECT item_id, user_id, SUM(total_price) as total, item_name, SUM (number) AS number FROM basket WHERE user_id = :userid GROUP BY item_id", userid=session["user_id"])

            if items2:
                #add all the items numbers first:
                num = 0
                for items in items2:
                    num += int(items["number"])
                #check if the seats on that date are already all taken
                seats_taken = db.execute("SELECT SUM(number) as taken FROM orders WHERE coll_day = :coll_day AND item_id BETWEEN 6 AND 7", coll_day=d2)
                #if seats taken is already null assign it an integer 0 so that operations can be made
                if seats_taken[0]["taken"] == None:
                    seats_taken[0]["taken"] = 0
                if (seats_taken[0]["taken"] + num) <= 85:
                    # if there are take the seats and insert them
                    seats = db.execute("SELECT item_id, user_id, SUM(total_price) as total, item_name, SUM (number) AS number FROM basket WHERE user_id = :userid AND item_id BETWEEN 6 AND 7 GROUP BY item_id", userid=session["user_id"])
                    if seats:
                        for seat in seats:
                            db.execute("INSERT INTO orders (item_id, user_id, coll_day, total_price, item_name, number, notes) VALUES (:item_id, :user_id, :coll_day, :total_price, :item_name, :number, :notes)",
                                               item_id=seat["item_id"], user_id=session.get("user_id"), coll_day=d2, total_price=seat["total"], item_name=seat["item_name"], number=seat["number"], notes=request.form.get("notes"))

                    # if seats are inserted or not take the item_id between the items that are not seats or event and insert them into database
                    items = db.execute("SELECT item_id, user_id, SUM(total_price) as total, item_name, SUM (number) AS number FROM basket WHERE user_id = :userid AND item_id NOT BETWEEN 6 and 7 GROUP BY item_id", userid=session["user_id"])
                    for item in items:
                        db.execute("INSERT INTO orders (item_id, user_id, coll_day, total_price, item_name, number, notes) VALUES (:item_id, :user_id, :coll_day, :total_price, :item_name, :number, :notes)",
                                   item_id=item["item_id"], user_id=session.get("user_id"), coll_day=d2, total_price=item["total"], item_name=item["item_name"], number=item["number"], notes=request.form.get("notes"))
                    db.execute("DELETE FROM basket WHERE user_id = :userid", userid = session["user_id"])

                    flash(f"Bought! Come and visit us on {d2.day}-{d2.month}-{d2.year}!")
                    return redirect(url_for("orders"))
                else:
                    db.execute("DELETE FROM basket WHERE user_id = :userid AND item_id BETWEEN 6 AND 7", userid=session["user_id"])
                    flash(f"Max number of seats (85) is being surpassed with your purchase. Current number of taken seats are {seats_taken[0]['taken']}. Please select a different number of seats.")
            else:
                flash("Can't check out with no items in shopping cart!")
        else:
            flash("The date has already passed!")

    #auto eliminate items that have 0 as number of them
    unused = db.execute("SELECT item_id, SUM(number) as number FROM basket WHERE user_id = :userid GROUP BY item_id HAVING number < 0", userid=session["user_id"])
    for items in unused:
        db.execute("DELETE FROM basket WHERE item_id = :item_id", item_id=items["item_id"])
    # now can select things to show in basket
    bought = db.execute("SELECT SUM(total_price) as total, item_name, SUM(number) as number, item_id FROM basket WHERE user_id = :userid GROUP BY item_id", userid=session["user_id"])
    if not bought:
        flash("Your basket is empty!")
    final_price = 0
    item_no = 0
    for items in bought:
        final_price += (int(items["total"]))
        item_no += 1
    return render_template("basket.html", bought=bought, final_price=final_price, item_no=item_no, now=now)


@app.route("/table/", methods=["GET", "POST"])
def table():
    # be able to select seats or book for event and put items in basket
    if request.method == "POST":
        # check if entered data is int or if data i entered at all
        if session.get("user_id") != None and (request.form.get("seats") or request.form.get("whole")):
            #check if whole is entered otherwise go to table
            if request.form.get("whole"):
                # I can insert the item 7 straight away because i already know it's event, without pulling from db
                db.execute("INSERT INTO basket (item_id, user_id, total_price, item_name, number) VALUES(:item_id, :user_id, :total_price, :item_name, :number)",
                           item_id=7, user_id=session.get("user_id"), total_price=65, item_name="event", number=85)
                flash("Full restaurant added to your basket, choose your date in the basket page.")
                return redirect(url_for("table"))

            #no if needed for the number of seats, all the checks already present
            try:
                num = int(request.form.get("seats"))
                # final price for the number of items, I already know each seat is 1 £
                final_price = 1 * num
                db.execute("INSERT INTO basket (item_id, user_id, total_price, item_name, number) VALUES(:item_id, :user_id, :total_price, :item_name, :number)",
                           item_id=6, user_id=session.get("user_id"), total_price=final_price, item_name="Seats", number=num)
                flash(f"{num} seats added to your basket, choose your date in the basket page.")
                return redirect(url_for("table"))
            except:
                flash("Input needs to be a number!")

        else:
            flash("Can't do that, there is no data or user logged in!")

    return render_template("table.html")


@app.route("/orders/", methods=["GET", "POST"])
@login_required
def orders():
    # just be able to see orders
    if session.get("user_id"):
        # could put everything in one line items and day.
        day = db.execute("SELECT SUM (number) as number, coll_day, SUM (total_price) as totalp_day FROM orders WHERE user_id = :userid GROUP BY coll_day ORDER BY coll_day", userid=session.get("user_id"))
        # GROUP_CONCAT is very useful for strings when using GROUP BY. https://stackoverflow.com/questions/149772/how-to-use-group-by-to-concatenate-strings-in-mysql
        items = db.execute("SELECT SUM(number) as number, item_name, SUM(total_price) as total_price, coll_day, GROUP_CONCAT(DISTINCT notes) as notes FROM orders WHERE user_id = :userid GROUP BY item_id, coll_day ORDER BY item_id", userid=session.get("user_id"))
        if not day:
            flash("You have no orders to show!")
        return render_template("orders.html", day=day, items=items)
    else:
        flash("Can't see that page if you are not logged in!")
        return redirect(url_for("login"))


@app.route("/admin_orders/", methods=["GET", "POST"])
@login_required
def admin_orders():
    # being able to see all orders from people ordered by name and being able to delete them
    if session["user_id"] == 1:
        if request.method == "POST":
            if request.form.get("delete"):
                now = datetime.now()
                d1 = datetime.date(now)
                db.execute("DELETE FROM orders WHERE coll_day < :now", now=d1)
            else:
                #delete all where the order date corresponds to the button pressed
                db.execute("DELETE FROM orders WHERE user_id = :userid AND coll_day = :coll_day", userid=request.form.get("userid"), coll_day=request.form.get("date"))
                return redirect(url_for("admin_orders"))
        # send the order date grouped by userid and innerjoin users to get the name for user_id
        # innerjoin explained here https://stackoverflow.com/questions/12129757/sql-query-get-name-from-another-table
        # remember that group by multiple items requires a ",""  not an "and"
        day = db.execute("SELECT SUM (t.number) AS number, t.coll_day AS coll_day, SUM (t.total_price) AS totalp_day, t.user_id AS user_id, u.username AS name FROM orders t INNER JOIN users u ON t.user_id = u.id GROUP BY t.user_id, t.coll_day ORDER BY t.coll_day, u.username")
        # same as for orders but needs to be for every person and also grouped by user_id
        items = db.execute("SELECT user_id, SUM(number) as number, item_name, SUM(total_price) AS total_price, coll_day, GROUP_CONCAT(DISTINCT notes) AS notes FROM orders GROUP BY item_id, coll_day, user_id ORDER BY item_id")
        return render_template("admin_orders.html", day=day, items=items)
    else:
        return redirect(url_for("index"))
