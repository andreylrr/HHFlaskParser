from flask import Blueprint, render_template, request, session, g, redirect, url_for, abort, flash

parser_blueprint = Blueprint("parser", __name__)


@parser_blueprint.route("/")
def root():
    return render_template("index.html")


@parser_blueprint.route("/index")
def index():
    return render_template("index.html")


@parser_blueprint.route("/history")
def history():
    return render_template("history.html")


@parser_blueprint.route("/requests")
def requests():
    return render_template("requests.html")
