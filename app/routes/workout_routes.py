from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Exercise, WorkoutLog
from app.forms import WorkoutLogForm
from datetime import datetime
from . import workout_bp as workout

@workout.route('/log', methods=['GET', 'POST'])
@login_required
def log():
    form = WorkoutLogForm()
    form.exercise.choices = [(e.id, e.name) for e in Exercise.query.filter_by(user_id=current_user.id).order_by(Exercise.name).all()]
    
    if form.validate_on_submit():
        workout_log = WorkoutLog(
            exercise_id=form.exercise.data,
            user_id=current_user.id,
            sets=form.sets.data,
            reps=form.reps.data,
            weight=form.weight.data,
            duration_minutes=form.duration_minutes.data,
            distance_km=form.distance_km.data,
            notes=form.notes.data
        )
        
        db.session.add(workout_log)
        db.session.commit()
        
        flash('Workout logged successfully!', 'success')
        return redirect(url_for('workout.history'))
    
    return render_template('log_workout.html', title='Log Workout', form=form)

@workout.route('/history')
@login_required
def history():
    logs = WorkoutLog.query.filter_by(user_id=current_user.id).order_by(WorkoutLog.date.desc()).all()
    return render_template('workout_history.html', title='Workout History', logs=logs)

@workout.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    log = WorkoutLog.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    db.session.delete(log)
    db.session.commit()
    
    flash('Workout log deleted successfully!', 'success')
    return redirect(url_for('workout.history'))

@workout.route('/<int:log_id>/edit', methods=['GET', 'POST'])
@login_required
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
        return redirect(url_for('workout.history'))
    
    return render_template('edit_workout.html',
                         title='Edit Workout Log',
                         form=form,
                         log_entry=log_entry) 