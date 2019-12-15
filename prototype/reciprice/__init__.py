from flask import Flask

from .extentions import csrf, mongo
from .main import main


def create_app(config_object='reciprice.settings'):
    app = Flask(__name__)
    app.config.from_object(config_object)

    csrf.init_app(app)
    mongo.init_app(app)

    app.register_blueprint(main)

    return app
