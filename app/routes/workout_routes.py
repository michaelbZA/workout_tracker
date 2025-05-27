from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Exercise, WorkoutLog
from app.forms import WorkoutLogForm
from datetime import datetime
from sqlalchemy import and_
from . import workout_bp as workout

@workout.route('/log', methods=['GET', 'POST'])
@login_required
def log():
    form = WorkoutLogForm()
    form.exercise.choices = [(e.id, e.name) for e in Exercise.query.filter_by(user_id=current_user.id).order_by(Exercise.name).all()]
    
    if form.validate_on_submit():
        exercise = Exercise.query.get(form.exercise.data)
        is_pr = form.is_pr.data
        
        # Check if this is a new personal best
        is_pb = False
        if exercise.category in ['arms', 'chest', 'back', 'legs', 'shoulders', 'core']:
            # For strength exercises, check if it's a new weight PB
            if form.weight.data:
                current_pb = WorkoutLog.query.filter(
                    and_(
                        WorkoutLog.user_id == current_user.id,
                        WorkoutLog.exercise_id == form.exercise.data,
                        WorkoutLog.is_pb == True
                    )
                ).order_by(WorkoutLog.weight.desc()).first()
                
                if not current_pb or form.weight.data > current_pb.weight:
                    is_pb = True
                    # If there was a previous PB, unmark it
                    if current_pb:
                        current_pb.is_pb = False
                        db.session.commit()
        
        elif exercise.category == 'cardio':
            # For cardio exercises, check if it's a new distance PB
            if form.distance_km.data:
                current_pb = WorkoutLog.query.filter(
                    and_(
                        WorkoutLog.user_id == current_user.id,
                        WorkoutLog.exercise_id == form.exercise.data,
                        WorkoutLog.is_pb == True
                    )
                ).order_by(WorkoutLog.distance_km.desc()).first()
                
                if not current_pb or form.distance_km.data > current_pb.distance_km:
                    is_pb = True
                    # If there was a previous PB, unmark it
                    if current_pb:
                        current_pb.is_pb = False
                        db.session.commit()
        
        workout_log = WorkoutLog(
            exercise_id=form.exercise.data,
            user_id=current_user.id,
            sets=form.sets.data,
            reps=form.reps.data,
            weight=form.weight.data,
            duration_minutes=form.duration_minutes.data,
            distance_km=form.distance_km.data,
            notes=form.notes.data,
            is_pb=is_pb,
            is_pr=is_pr,
            pr_description=form.pr_description.data if is_pr else None
        )
        
        db.session.add(workout_log)
        db.session.commit()
        
        if is_pb:
            flash('New personal best achieved!', 'success')
        if is_pr:
            flash('New personal record logged!', 'success')
        if not is_pb and not is_pr:
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
    
    # If deleting a PB, we need to find the next best workout and mark it as PB
    if log.is_pb:
        exercise = log.exercise
        if exercise.category in ['arms', 'chest', 'back', 'legs', 'shoulders', 'core']:
            next_best = WorkoutLog.query.filter(
                and_(
                    WorkoutLog.user_id == current_user.id,
                    WorkoutLog.exercise_id == exercise.id,
                    WorkoutLog.id != log.id
                )
            ).order_by(WorkoutLog.weight.desc()).first()
        else:  # cardio
            next_best = WorkoutLog.query.filter(
                and_(
                    WorkoutLog.user_id == current_user.id,
                    WorkoutLog.exercise_id == exercise.id,
                    WorkoutLog.id != log.id
                )
            ).order_by(WorkoutLog.distance_km.desc()).first()
        
        if next_best:
            next_best.is_pb = True
    
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
        exercise = Exercise.query.get(form.exercise.data)
        is_pr = form.is_pr.data
        
        # Check if this is a new personal best
        is_pb = False
        if exercise.category in ['arms', 'chest', 'back', 'legs', 'shoulders', 'core']:
            # For strength exercises, check if it's a new weight PB
            if form.weight.data:
                current_pb = WorkoutLog.query.filter(
                    and_(
                        WorkoutLog.user_id == current_user.id,
                        WorkoutLog.exercise_id == form.exercise.data,
                        WorkoutLog.is_pb == True,
                        WorkoutLog.id != log_id  # Exclude current log
                    )
                ).order_by(WorkoutLog.weight.desc()).first()
                
                if not current_pb or form.weight.data > current_pb.weight:
                    is_pb = True
                    # If there was a previous PB, unmark it
                    if current_pb:
                        current_pb.is_pb = False
                        db.session.commit()
        
        elif exercise.category == 'cardio':
            # For cardio exercises, check if it's a new distance PB
            if form.distance_km.data:
                current_pb = WorkoutLog.query.filter(
                    and_(
                        WorkoutLog.user_id == current_user.id,
                        WorkoutLog.exercise_id == form.exercise.data,
                        WorkoutLog.is_pb == True,
                        WorkoutLog.id != log_id  # Exclude current log
                    )
                ).order_by(WorkoutLog.distance_km.desc()).first()
                
                if not current_pb or form.distance_km.data > current_pb.distance_km:
                    is_pb = True
                    # If there was a previous PB, unmark it
                    if current_pb:
                        current_pb.is_pb = False
                        db.session.commit()
        
        log_entry.exercise_id = form.exercise.data
        log_entry.sets = form.sets.data
        log_entry.reps = form.reps.data
        log_entry.weight = form.weight.data
        log_entry.duration_minutes = form.duration_minutes.data
        log_entry.distance_km = form.distance_km.data
        log_entry.notes = form.notes.data
        log_entry.is_pb = is_pb
        log_entry.is_pr = is_pr
        log_entry.pr_description = form.pr_description.data if is_pr else None
        
        db.session.commit()
        
        if is_pb and not log_entry.is_pb:
            flash('New personal best achieved!', 'success')
        if is_pr and not log_entry.is_pr:
            flash('New personal record set!', 'success')
        if not is_pb and not is_pr:
            flash('Workout log updated successfully!', 'success')
        return redirect(url_for('workout.history'))
    
    return render_template('edit_workout.html',
                         title='Edit Workout Log',
                         form=form,
                         log_entry=log_entry) 