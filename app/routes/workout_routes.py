from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Exercise, WorkoutLog
from app.forms import WorkoutLogForm
from datetime import datetime
from . import workout_bp as workout

@workout.route('/workouts/log', methods=['GET', 'POST'])
@login_required
def log():
    if request.method == 'POST':
        exercise_id = request.form.get('exercise_id')
        sets = request.form.get('sets')
        reps = request.form.get('reps')
        weight = request.form.get('weight')
        duration_minutes = request.form.get('duration_minutes')
        distance_km = request.form.get('distance_km')
        notes = request.form.get('notes')
        
        exercise = Exercise.query.filter_by(id=exercise_id, user_id=current_user.id).first_or_404()
        
        workout_log = WorkoutLog(
            exercise_id=exercise_id,
            user_id=current_user.id,
            sets=sets if sets else None,
            reps=reps if reps else None,
            weight=weight if weight else None,
            duration_minutes=duration_minutes if duration_minutes else None,
            distance_km=distance_km if distance_km else None,
            notes=notes
        )
        
        db.session.add(workout_log)
        db.session.commit()
        
        flash('Workout logged successfully!', 'success')
        return redirect(url_for('workout.history'))
    
    exercises = Exercise.query.filter_by(user_id=current_user.id).order_by(Exercise.name).all()
    return render_template('log_workout.html', title='Log Workout', exercises=exercises)

@workout.route('/workouts/history')
@login_required
def history():
    logs = WorkoutLog.query.filter_by(user_id=current_user.id).order_by(WorkoutLog.date.desc()).all()
    return render_template('workout_history.html', title='Workout History', logs=logs)

@workout.route('/workouts/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    log = WorkoutLog.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    db.session.delete(log)
    db.session.commit()
    
    flash('Workout log deleted successfully!', 'success')
    return redirect(url_for('workout.history'))

@workout.route('/<int:log_id>/edit', methods=['GET', 'POST'])
def edit(log_id):
    log_entry = WorkoutLog.query.get_or_404(log_id)
    form = WorkoutLogForm(obj=log_entry)
    form.exercise.choices = [(e.id, e.name) for e in Exercise.query.order_by(Exercise.name).all()]
    
    if form.validate_on_submit():
        log_entry.exercise_id = form.exercise.data
        log_entry.sets = form.sets.data
        log_entry.reps = form.reps.data
        log_entry.weight = form.weight.data
        log_entry.duration_minutes = form.duration_minutes.data
        log_entry.distance_km = form.distance_km.data
        log_entry.notes = form.notes.data
        
        db.session.commit()
        flash('Workout log updated successfully!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('edit_workout.html',
                         title='Edit Workout Log',
                         form=form,
                         log_entry=log_entry) 