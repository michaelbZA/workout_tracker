# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash
from app import db
from app.models import Exercise, WorkoutLog # Import WorkoutLog model
from app.forms import ExerciseForm, WorkoutLogForm # Import WorkoutLogForm
from datetime import datetime, timezone # For default date

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    exercises = Exercise.query.order_by(Exercise.name).all()
    # Query workout logs, ordered by date descending (most recent first)
    # .join(Exercise) allows access to exercise.name in the template
    workout_logs = WorkoutLog.query.join(Exercise).order_by(WorkoutLog.date.desc()).all()
    return render_template('index.html', title='Home', exercises=exercises, workout_logs=workout_logs)

@bp.route('/add_exercise', methods=['GET', 'POST'])
def add_exercise():
    form = ExerciseForm()
    if form.validate_on_submit():
        exercise = Exercise(name=form.name.data,
                            description=form.description.data,
                            category=form.category.data)
        db.session.add(exercise)
        db.session.commit()
        flash('Exercise added successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_exercise.html', title='Add Exercise', form=form)

@bp.route('/log_workout', methods=['GET', 'POST'])
def log_workout():
    form = WorkoutLogForm()
    # Populate the choices for the exercise SelectField
    # choices should be a list of tuples: (value, label)
    # Here, value is exercise.id, label is exercise.name
    form.exercise.choices = [(e.id, e.name) for e in Exercise.query.order_by(Exercise.name).all()]

    if form.validate_on_submit():
        # Get the selected exercise ID from the form
        exercise_id = form.exercise.data
        # Fetch the corresponding Exercise object (or handle if not found, though DataRequired should prevent this)
        selected_exercise = Exercise.query.get(exercise_id)

        if selected_exercise:
            log_entry = WorkoutLog(
                exercise_id=selected_exercise.id, # or simply form.exercise.data
                # date is handled by default in the model for now
                sets=form.sets.data,
                reps=form.reps.data,
                weight=form.weight.data,
                duration_minutes=form.duration_minutes.data,
                distance_km=form.distance_km.data,
                notes=form.notes.data
                # is_pb logic will be more complex, handle later
            )
            db.session.add(log_entry)
            db.session.commit()
            flash(f'Workout for {selected_exercise.name} logged successfully!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Selected exercise not found.', 'error') # Should not happen with current setup

    return render_template('log_workout.html', title='Log Workout', form=form)