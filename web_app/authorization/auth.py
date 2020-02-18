from flask import Blueprint, render_template, request, session, g, redirect, url_for, abort, flash
import hashlib, binascii, os

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["FirstName"]
        lastname = request.form["LastName"]
        email = request.form["Email"]
        password = request.form["Password"]
        repeat_password = request.form["RepeatPassword"]
        if password != repeat_password:
            flash("Ошибка при вводе паролей")
        else:
            h_password = hash_password(password)
            cur = g.db.cursor()
            sql = "INSERT INTO users (name, last_name, email, password, created) VALUES (?,?,?,?, datetime('now', 'localtime'))"
            cur.execute(sql, (username, lastname, email, h_password))
            g.db.commit()
            return redirect("login")
    return render_template("register.html")


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["Email"]
        password = request.form["Password"]
        cur = g.db.cursor()
        sql = "SELECT id, name, password FROM USERS WHERE email=?"
        cur.execute(sql, (email,))
        row = cur.fetchone()
        if not row:
            flash("Такой пользователь не зарегестрирован.")
        else:
            user_id = row[0]
            user_name = row[1]
            h_password = row[2]
            if verify_password(h_password, password):
                session["user_name"] = user_name
                session["user_id"] = user_id
                return redirect("index")
            else:
                flash("Указан неверный пароль")

    return render_template("login.html")


@auth_blueprint.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    return render_template("forgot-password.html")

@auth_blueprint.route("/contacts", methods=["GET", "POST"])
def contacts():
    return render_template("contacts.html")


def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password