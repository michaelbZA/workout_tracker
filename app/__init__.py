# app/__init__.py
from flask import Flask
import os # Import os for instance path

def create_app(test_config=None):
    # Create and configure the app
    # __name__ is the name of the current Python module.
    # instance_relative_config=True tells the app that configuration files are relative to the instance folder.
    app = Flask(__name__, instance_relative_config=True)

    # Default configuration
    # SECRET_KEY is used by Flask and extensions to keep data safe. Set it to a random string.
    # DATABASE is the path where the SQLite database file will be stored.
    app.config.from_mapping(
        SECRET_KEY='dev', # CHANGE THIS to a random secret key for production!
        DATABASE=os.path.join(app.instance_path, 'workout_tracker.sqlite'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        # You can put overrides here in a config.py file in the instance folder
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # Already exists

    # A simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # Import and register blueprints for routes later (e.g., from routes.py)
    # from . import routes
    # app.register_blueprint(routes.bp)

    return app