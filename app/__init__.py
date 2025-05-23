# app/__init__.py
from flask import Flask
import os

# We'll add database initialisation here later
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate

# db = SQLAlchemy()
# migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', # CHANGE THIS for production!
        DATABASE=os.path.join(app.instance_path, 'workout_tracker.sqlite'),
        # Add SQLAlchemy configurations later
        # SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'workout_tracker.sqlite'),
        # SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions here later
    # db.init_app(app)
    # migrate.init_app(app, db)

    # Remove the old /hello route from here
    # @app.route('/hello')
    # def hello():
    #     return 'Hello, World!'

    # Import and register the blueprint from routes.py
    from . import routes  # This imports routes.py from the current package (app)
    app.register_blueprint(routes.bp)

    # If you had other blueprints, you would register them here too
    # from . import auth
    # app.register_blueprint(auth.bp)

    return app