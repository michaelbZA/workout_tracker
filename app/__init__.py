# app/__init__.py
from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from datetime import datetime
import json

# Create database extension objects BEFORE the create_app function
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

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
    login_manager.init_app(app) # Initialize Flask-Login
    login_manager.login_view = 'auth.login' # Set the login view
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Add this context processor
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # Add the fromjson filter
    def fromjson_filter(value):
        return json.loads(value)
    app.jinja_env.filters['fromjson'] = fromjson_filter

    # Import and register blueprints
    from .routes import init_app as init_routes
    init_routes(app)
    
    # Import models here so that Flask-Migrate can find them
    from . import models

    return app