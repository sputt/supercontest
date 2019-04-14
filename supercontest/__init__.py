# pylint: disable=cyclic-import
# This toplevel package imports some modules to build the app.
# but it's protected by the get_app function, which is not called here
# but my the modules themselves.
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_user import UserManager
from flask_wtf.csrf import CSRFProtect
from wtforms.fields import HiddenField

# pylint: disable=invalid-name
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
csrf_protect = CSRFProtect()
# pylint: enable=invalid-name


def is_hidden_field_filter(field):
    return isinstance(field, HiddenField)


def get_headerless_conf(pth):
    with open(pth) as filehandle:
        content = filehandle.readlines()
    return {line.split('=')[0]:line.split('=')[1].strip() for line in content
            if not line.startswith('#')}


def get_app():
    curdir = os.path.dirname(os.path.abspath(__file__))

    app = Flask(__name__)
    app.config.from_pyfile(os.path.join(curdir, 'config', 'public.py'))
    app.config.from_pyfile(os.path.join(curdir, 'config', 'private.py'))

    # The flask app reads the database configs directly, rather than being passed them
    # through the env in docker. This means runserver and other debug/dev methods
    # aren't FULLY coupled to docker-compose. Runserver still won't work because it now expects
    # the db in another container on a certain port, but you can still use it for
    # light smoketesting.
    db_conf_dir = os.path.join(curdir, '..', 'docker', 'database')
    db_public_conf = get_headerless_conf(os.path.join(db_conf_dir, 'public.conf'))
    db_private_conf = get_headerless_conf(os.path.join(db_conf_dir, 'private.conf'))
    db_conf = {**db_public_conf, **db_private_conf}
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'postgresql://{user}:{password}@{host}:{port}/{database}'.format(
            user=db_conf['POSTGRES_USER'],
            password=db_conf['POSTGRES_PASSWORD'],
            host=db_conf['POSTGRES_HOST'],
            port=db_conf['POSTGRES_PORT'],
            database=db_conf['POSTGRES_DB'])

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf_protect.init_app(app)

    from supercontest.views import register_blueprints  # pylint: disable=wrong-import-position
    register_blueprints(app)

    from supercontest.models import User  # pylint: disable=wrong-import-position
    user_manager = UserManager(app, db, User)

    app.jinja_env.globals['bootstrap_is_hidden_field'] = is_hidden_field_filter  # pylint: disable=no-member

    @app.context_processor
    def context_processor():  # pylint: disable=unused-variable
        return dict(user_manager=user_manager)

    return app
