from .views import main_blueprint, week_blueprint


def register_blueprints(app):
    app.register_blueprint(main_blueprint)
    app.register_blueprint(week_blueprint)
