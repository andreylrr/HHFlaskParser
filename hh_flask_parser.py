import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import os

# configuration
DATABASE = 'Database/hh_flask.sqlite'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route("/")
def root():
    return render_template("404.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/contacts")
def contacts():
    return render_template("contacts.html")

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot-password.html")

@app.route("/history")
def history():
    return render_template("history.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/requests")
def requests():
    return render_template("requests.html")


if __name__ == "__main__":

    app.run()