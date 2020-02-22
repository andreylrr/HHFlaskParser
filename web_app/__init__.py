from flask import Flask

# configuration
DEBUG = True
SECRET_KEY = b'\x143#\x1eV;\xc9\xa0\xecr\r\xd4/{b\n'

app = Flask(__name__)
app.config.from_object(__name__)

def create_app():
    from web_app.authorization.auth import auth_blueprint
    from web_app.flask_parser.flask_parser import parser_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(parser_blueprint)
    return app

