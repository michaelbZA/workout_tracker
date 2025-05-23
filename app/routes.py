# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash
from app import db # Import db from app/__init__.py
from app.models import Exercise # Import your Exercise model
from app.forms import ExerciseForm # Import your new form

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    # We'll query and display exercises and logs here later
    exercises = Exercise.query.order_by(Exercise.name).all()
    return render_template('index.html', title='Home', exercises=exercises)

@bp.route('/add_exercise', methods=['GET', 'POST'])
def add_exercise():
    form = ExerciseForm()
    if form.validate_on_submit():
        # Form has been submitted and validated
        exercise = Exercise(name=form.name.data,
                            description=form.description.data,
                            category=form.category.data)
        db.session.add(exercise)
        db.session.commit()
        flash('Exercise added successfully!', 'success') # 'success' is a category for styling
        return redirect(url_for('main.index')) # Redirect to homepage after adding
    # If GET request or form validation fails, render the form page
    return render_template('add_exercise.html', title='Add Exercise', form=form)

# ... (other routes if you had them)