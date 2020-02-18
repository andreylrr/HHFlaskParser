import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import os
from flask_loginmanager import LoginManager
from web_app.authorization.auth import auth_blueprint
from web_app.flask_parser.flask_parser import parser_blueprint


# configuration
DATABASE = '../Database/hh_flask.sqlite'
DEBUG = True
SECRET_KEY = b'\x143#\x1eV;\xc9\xa0\xecr\r\xd4/{b\n'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)
app.register_blueprint(auth_blueprint)
app.register_blueprint(parser_blueprint)
login_manager = LoginManager()
login_manager.init_app(app)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()