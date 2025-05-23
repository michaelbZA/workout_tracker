# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request  # Add request here
from app import db
from app.models import Exercise, WorkoutLog
from app.forms import ExerciseForm, WorkoutLogForm
from datetime import datetime, timezone
from sqlalchemy import func
from flask import jsonify
import json
from sqlalchemy.exc import IntegrityError  # Add this if not already present

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

@bp.route('/exercise/<int:exercise_id>/progress')
def exercise_progress(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    logs = WorkoutLog.query.filter_by(exercise_id=exercise.id).order_by(WorkoutLog.date.asc()).all()

    chart_data = {
        'labels': [], # Dates
        'datasets': []
    }

    dataset_label = ""
    data_points = []

    # Determine chart type based on category (simple heuristic)
    is_cardio = exercise.category and 'cardio' in exercise.category.lower()

    if is_cardio:
        dataset_label = 'Distance (km)'
        for log in logs:
            if log.distance_km is not None:
                chart_data['labels'].append(log.date.strftime('%Y-%m-%d'))
                data_points.append(log.distance_km)
        # You could add another dataset for duration if desired
        # e.g., duration_data_points = [log.duration_minutes for log in logs if log.duration_minutes is not None]
    else: # Assume strength/weight-based
        dataset_label = 'Weight Lifted'
        for log in logs:
            if log.weight is not None:
                # To avoid too many points if multiple sets on same day,
                # you might want to aggregate (e.g., max weight per day).
                # For now, plotting each log entry with weight.
                chart_data['labels'].append(log.date.strftime('%Y-%m-%d %H:%M')) # More granular for multiple entries per day
                data_points.append(log.weight)

    if data_points: # Only add dataset if there's data
        chart_data['datasets'].append({
            'label': dataset_label,
            'data': data_points,
            'fill': False,
            'borderColor': 'rgb(75, 192, 192)',
            'tension': 0.1
        })

    # Safely pass chart_data to template by converting to JSON string
    chart_data_json = json.dumps(chart_data)

    return render_template('exercise_progress.html',
                           title=f"{exercise.name} Progress",
                           exercise=exercise,
                           chart_data_json=chart_data_json)

@bp.route('/delete_log/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    log_to_delete = WorkoutLog.query.get_or_404(log_id)
    # Future enhancement: Add ownership check if you implement user accounts
    # if log_to_delete.author != current_user:
    #     abort(403) # Forbidden

    exercise_name = log_to_delete.exercise.name # Get name before deleting for the flash message
    try:
        db.session.delete(log_to_delete)
        db.session.commit()
        flash(f'Workout log for "{exercise_name}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback() # Rollback in case of error
        flash(f'Error deleting workout log: {str(e)}', 'error')

    return redirect(url_for('main.index'))

@bp.route('/edit_log/<int:log_id>', methods=['GET', 'POST'])
def edit_log(log_id):
    log_to_edit = WorkoutLog.query.get_or_404(log_id)
    # Future enhancement: Add ownership check for user accounts
    # if log_to_edit.author != current_user:
    # abort(403)

    form = WorkoutLogForm(obj=log_to_edit) # Pre-populate form with log_to_edit data
    # The obj=log_to_edit will try to match attribute names.
    # For the SelectField 'exercise', its data attribute will be set to log_to_edit.exercise_id.

    # Populate exercise choices
    form.exercise.choices = [(e.id, e.name) for e in Exercise.query.order_by(Exercise.name).all()]
    # Ensure the current exercise is selected if form is being populated from obj
    # WTForms should handle setting the SelectField's data/value correctly if `obj` is passed
    # and the `exercise` field in the form is correctly named and its data corresponds to one of the choices' values.
    # When `obj` is passed to the form constructor, for a field named `exercise`,
    # it will look for `log_to_edit.exercise`. If `log_to_edit.exercise` is the Exercise object,
    # then `log_to_edit.exercise.id` would be the value.
    # Since our WorkoutLogForm has an `exercise` field which expects an exercise ID,
    # we need to make sure the form's `exercise.data` is correctly set to `log_to_edit.exercise_id`
    # when it's initially populated. Passing `obj=log_to_edit` and having `form.exercise.data = log_to_edit.exercise_id`
    # (which would happen if `log_to_edit.exercise` was the ID itself, or if the field was named `exercise_id`)
    # is what we want.
    # Let's ensure the form's exercise field is correctly populated for the GET request.
    # When `obj` is used, WTForms will try to get `obj.exercise`. If `log_to_edit.exercise` is the actual `Exercise` object (due to relationship),
    # then `form.exercise.data` might be this object. We need it to be the ID.
    # The `coerce=int` on SelectField helps.

    if form.validate_on_submit():
        try:
            log_to_edit.exercise_id = form.exercise.data
            log_to_edit.sets = form.sets.data
            log_to_edit.reps = form.reps.data
            log_to_edit.weight = form.weight.data
            log_to_edit.duration_minutes = form.duration_minutes.data
            log_to_edit.distance_km = form.distance_km.data
            log_to_edit.notes = form.notes.data
            # If you added a date field to the form:
            # log_to_edit.date = form.date.data

            db.session.commit()
            flash('Workout log updated successfully!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating workout log: {str(e)}', 'error')
    elif request.method == 'GET':
        # Pre-populate form fields from the existing log entry for GET request
        # The `obj=log_to_edit` in form instantiation already does this for matching field names.
        # For the 'exercise' SelectField, its value should be the exercise_id.
        form.exercise.data = log_to_edit.exercise_id # Ensure current exercise is selected
        form.sets.data = log_to_edit.sets
        form.reps.data = log_to_edit.reps
        form.weight.data = log_to_edit.weight
        form.duration_minutes.data = log_to_edit.duration_minutes
        form.distance_km.data = log_to_edit.distance_km
        form.notes.data = log_to_edit.notes
        # If you add a date field to the form:
        # form.date.data = log_to_edit.date

    return render_template('edit_log.html', title='Edit Workout Log', form=form, log_id=log_id)

@bp.route('/delete_exercise/<int:exercise_id>', methods=['POST'])
def delete_exercise(exercise_id):
    exercise_to_delete = Exercise.query.get_or_404(exercise_id)

    # Check if there are any workout logs associated with this exercise
    if exercise_to_delete.workout_logs: # This uses the backref from WorkoutLog model
        flash(f'Cannot delete "{exercise_to_delete.name}" because it has associated workout logs. Please delete or reassign those logs first.', 'error')
    else:
        try:
            db.session.delete(exercise_to_delete)
            db.session.commit()
            flash(f'Exercise "{exercise_to_delete.name}" deleted successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting exercise: {str(e)}', 'error')

    return redirect(url_for('main.index'))

@bp.route('/edit_exercise/<int:exercise_id>', methods=['GET', 'POST'])
def edit_exercise(exercise_id):
    exercise_to_edit = Exercise.query.get_or_404(exercise_id)
    form = ExerciseForm(obj=exercise_to_edit) # Pre-populate form

    if form.validate_on_submit():
        # Check if the new name conflicts with an existing exercise name (excluding itself)
        new_name = form.name.data
        existing_exercise_with_name = Exercise.query.filter(Exercise.name == new_name, Exercise.id != exercise_id).first()
        if existing_exercise_with_name:
            flash('An exercise with this name already exists. Please choose a different name.', 'error')
        else:
            try:
                exercise_to_edit.name = new_name
                exercise_to_edit.description = form.description.data
                exercise_to_edit.category = form.category.data
                db.session.commit()
                flash('Exercise updated successfully!', 'success')
                return redirect(url_for('main.index'))
            except IntegrityError: # Should be caught by the explicit check above, but as a fallback
                db.session.rollback()
                flash('An exercise with this name already exists (database error). Please choose a different name.', 'error')
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating exercise: {str(e)}', 'error')
    elif request.method == 'GET':
        # Form is already pre-populated by obj=exercise_to_edit
        # If you had fields not directly matching attributes, you'd set them here:
        # form.name.data = exercise_to_edit.name
        # form.description.data = exercise_to_edit.description
        # form.category.data = exercise_to_edit.category
        pass # No need to explicitly set form data here if obj works as expected

    return render_template('edit_exercise.html', title='Edit Exercise', form=form, exercise_id=exercise_id)