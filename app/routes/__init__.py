from flask import Blueprint

# Create blueprints
main_bp = Blueprint('main', __name__)
exercise_bp = Blueprint('exercise', __name__, url_prefix='/exercise')
workout_bp = Blueprint('workout', __name__, url_prefix='/workout')

# Import routes after creating blueprints to avoid circular imports
from . import main_routes
from . import exercise_routes
from . import workout_routes
from . import auth_routes
from . import analytics_routes

def init_app(app):
    """Register all blueprints with the application."""
    app.register_blueprint(main_bp)
    app.register_blueprint(exercise_bp)
    app.register_blueprint(workout_bp)
    app.register_blueprint(auth_routes.auth)
    app.register_blueprint(analytics_routes.analytics_bp) 