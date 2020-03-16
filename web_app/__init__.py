from flask import Flask, render_template
from flask_mail import Mail, Message

# configuration
DEBUG = True
SECRET_KEY = b'\x143#\x1eV;\xc9\xa0\xecr\r\xd4/{b\n'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'andreylrr@gmail.com'
MAIL_PASSWORD = 'xxxxxxxx'

app = Flask(__name__)
app.config.from_object(__name__)

def create_app():
    from web_app.authorization.auth import auth_blueprint
    from web_app.flask_parser.flask_parser import parser_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(parser_blueprint)
    return app


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")
