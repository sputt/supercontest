import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_user import UserManager

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


class UriConfig(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        os.path.dirname(os.path.abspath(os.path.dirname(__file__))),
        'data', 'supercontest.db')


def get_app():
    app = Flask(__name__)
    app.config.from_pyfile('config_public.py')
    app.config.from_pyfile('config_private.py')
    app.config.from_object(UriConfig)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    from supercontest.models import User  # pylint: disable=wrong-import-position
    user_manager = UserManager(app, db, User)  # pylint: disable=unused-variable

    from supercontest.views import register_blueprints  # pylint: disable=wrong-import-position
    register_blueprints(app)

    return app
