from flask import Flask

from .extentions import csrf, mongo
from .main import main
from . import models


def create_app(config_object='reciprice.settings'):
    app = Flask(__name__)
    app.config.from_object(config_object)

    csrf.init_app(app)
    mongo.init_app(app)

    app.register_blueprint(main)

    print('Created app with %s users.' % models.user_count())

    return app
