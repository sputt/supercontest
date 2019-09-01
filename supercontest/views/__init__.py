from .views import season_week_blueprint, main_blueprint


def register_blueprints(app):
    app.register_blueprint(season_week_blueprint)
    app.register_blueprint(main_blueprint)
