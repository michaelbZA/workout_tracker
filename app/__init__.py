# app/__init__.py
from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Create database extension objects BEFORE the create_app function
db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', # CHANGE THIS for production!
        # DATABASE config for SQLite (used by Flask-SQLAlchemy)
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'workout_tracker.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False, # Disables a feature that signals the application every time a change is about to be made in the database.
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions WITH the app object
    db.init_app(app)
    migrate.init_app(app, db) # Initialize Flask-Migrate

    from . import routes
    app.register_blueprint(routes.bp)

    # Import models here so that Flask-Migrate can find them
    from . import models

    return app