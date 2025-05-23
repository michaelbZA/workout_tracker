# app/routes.py
from flask import Blueprint, render_template
from datetime import datetime

# Create a Blueprint. A blueprint is a way to organize a group of related views and other code.
# 'main' is the name of this blueprint.
bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    # render_template will look for HTML files in the 'templates' folder.
    return render_template('index.html', title='Home', now=datetime.utcnow())

# You can add more routes here later
# For example, a route to add a new workout:
# @bp.route('/add_workout')
# def add_workout():
#     return "This will be the page to add workouts."