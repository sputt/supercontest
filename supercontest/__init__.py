import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_user import UserManager
from flask_wtf.csrf import CSRFProtect
from wtforms.fields import HiddenField

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
csrf_protect = CSRFProtect()


def is_hidden_field_filter(field):
    return isinstance(field, HiddenField)


def get_app():
    app = Flask(__name__)
    app.config.from_pyfile(os.path.join('config', 'public.py'))
    app.config.from_pyfile(os.path.join('config', 'private.py'))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://supercontest:{}@localhost/supercontest'.format(app.config['MAIL_PASSWORD'])

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf_protect.init_app(app)

    from supercontest.views import register_blueprints  # pylint: disable=wrong-import-position
    register_blueprints(app)

    from supercontest.models import User  # pylint: disable=wrong-import-position
    user_manager = UserManager(app, db, User)

    app.jinja_env.globals['bootstrap_is_hidden_field'] = is_hidden_field_filter

    @app.context_processor
    def context_processor():
        return dict(user_manager=user_manager)

    return app
