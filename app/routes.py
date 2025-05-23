# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash
from app import db
from app.models import Exercise, WorkoutLog
from app.forms import ExerciseForm, WorkoutLogForm
from datetime import datetime, timezone
from sqlalchemy import func # For using functions like MAX

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    exercises = Exercise.query.order_by(Exercise.name).all()
    workout_logs = WorkoutLog.query.join(Exercise).order_by(WorkoutLog.date.desc()).all()

    # --- PB Calculation Logic ---
    personal_bests = {}
    for ex in exercises:
        pb_data = {}
        # Max Weight PB
        # Find the log entry with the maximum weight for this exercise,
        # ensuring weight is not None.
        max_weight_log = WorkoutLog.query.filter(
                                WorkoutLog.exercise_id == ex.id,
                                WorkoutLog.weight.isnot(None)
                            ).order_by(WorkoutLog.weight.desc(), WorkoutLog.date.desc()).first()
        if max_weight_log:
            pb_data['max_weight'] = {
                'value': max_weight_log.weight,
                'date': max_weight_log.date,
                'reps': max_weight_log.reps, # Also show reps for context
                'sets': max_weight_log.sets  # And sets
            }

        # Longest Distance PB (e.g., if category is 'Cardio')
        # We'll make a simple assumption for now: if "Cardio" is in the category name.
        if ex.category and 'cardio' in ex.category.lower():
            max_distance_log = WorkoutLog.query.filter(
                                    WorkoutLog.exercise_id == ex.id,
                                    WorkoutLog.distance_km.isnot(None)
                                ).order_by(WorkoutLog.distance_km.desc(), WorkoutLog.date.desc()).first()
            if max_distance_log:
                pb_data['max_distance'] = {
                    'value': max_distance_log.distance_km,
                    'date': max_distance_log.date,
                    'duration': max_distance_log.duration_minutes # Also show duration
                }

        if pb_data: # Only add if we found any PB for this exercise
            personal_bests[ex.id] = pb_data
    # --- End PB Calculation Logic ---

    return render_template('index.html',
                           title='Home',
                           exercises=exercises,
                           workout_logs=workout_logs,
                           personal_bests=personal_bests) # Pass PBs to template

# ... (add_exercise and log_workout routes remain the same) ...
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
    form.exercise.choices = [(e.id, e.name) for e in Exercise.query.order_by(Exercise.name).all()]

    if form.validate_on_submit():
        exercise_id = form.exercise.data
        selected_exercise = Exercise.query.get(exercise_id)

        if selected_exercise:
            log_entry = WorkoutLog(
                exercise_id=selected_exercise.id,
                sets=form.sets.data,
                reps=form.reps.data,
                weight=form.weight.data,
                duration_minutes=form.duration_minutes.data,
                distance_km=form.distance_km.data,
                notes=form.notes.data
            )
            db.session.add(log_entry)
            db.session.commit()
            flash(f'Workout for {selected_exercise.name} logged successfully!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Selected exercise not found.', 'error')

    return render_template('log_workout.html', title='Log Workout', form=form)