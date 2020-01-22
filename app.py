from flask import Flask, render_template, make_response, url_for, jsonify, redirect, session, flash, request
from cs50 import SQL
from flask_session import Session
from datetime import datetime
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tavernetta.db"
db = SQL("sqlite:///finance.db")

app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
def index():
    # Todo
    return render_template ("index.html")

@app.route("/login")
def login():
    # Todo
    return render_template ("login.html")

@app.route("/logout")
def logout():
    # Todo
    return

@app.route("/register")
def register():
    # Todo
    return render_template ("register.html")

@app.route("/table")
def table():
    # Todo
    return render_template ("table.html")

@app.route("/basket")
def basket():
    # Todo
    return render_template ("basket.html")

@app.route("/menu")
def menu():
    # Todo
    return render_template ("menu.html")

@app.route("/orders")
def orders():
    # Todo
    return render_template ("orders.html")

if __name__ == "__main__":
    app.run(debug = True)