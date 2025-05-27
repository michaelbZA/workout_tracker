from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Exercise, WorkoutLog
from app.forms import ExerciseForm
from datetime import datetime
import json
from . import exercise_bp as exercise

@exercise.route('/exercises')
@login_required
def list():
    exercises = Exercise.query.filter_by(user_id=current_user.id).order_by(Exercise.name).all()
    return render_template('exercise_list.html', title='Exercises', exercises=exercises)

@exercise.route('/exercises/add', methods=['GET', 'POST'])
@login_required
def add():
    form = ExerciseForm()
    if form.validate_on_submit():
        exercise = Exercise(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            user_id=current_user.id
        )
        db.session.add(exercise)
        db.session.commit()
        flash('Exercise added successfully!', 'success')
        return redirect(url_for('exercise.list'))
    return render_template('add_exercise.html', title='Add Exercise', form=form)

@exercise.route('/exercises/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    exercise = Exercise.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = ExerciseForm()
    
    if request.method == 'GET':
        form.name.data = exercise.name
        form.description.data = exercise.description
        form.category.data = exercise.category
    
    if form.validate_on_submit():
        existing = Exercise.query.filter_by(name=form.name.data, user_id=current_user.id).first()
        if existing and existing.id != id:
            flash('An exercise with this name already exists.', 'error')
            return redirect(url_for('exercise.edit', id=id))
        
        exercise.name = form.name.data
        exercise.description = form.description.data
        exercise.category = form.category.data
        
        db.session.commit()
        
        flash('Exercise updated successfully!', 'success')
        return redirect(url_for('exercise.list'))
    
    return render_template('edit_exercise.html', title='Edit Exercise', exercise=exercise, form=form)

@exercise.route('/exercises/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    exercise = Exercise.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Delete associated workout logs
    WorkoutLog.query.filter_by(exercise_id=id).delete()
    
    db.session.delete(exercise)
    db.session.commit()
    
    flash('Exercise deleted successfully!', 'success')
    return redirect(url_for('exercise.list'))

@exercise.route('/exercises/<int:id>/progress')
@login_required
def progress(id):
    exercise = Exercise.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    logs = WorkoutLog.query.filter_by(exercise_id=id).order_by(WorkoutLog.date).all()
    
    chart_labels = []
    data_points = []
    
    # Styling arrays for Chart.js points
    point_radii = []
    point_background_colors = []
    point_border_colors = []

    default_point_radius = 4
    pb_point_radius = 7
    default_point_bg_color = 'rgba(75, 192, 192, 0.6)'
    pb_point_bg_color = 'rgba(255, 99, 132, 1)'
    default_point_border_color = 'rgba(75, 192, 192, 1)'
    pb_point_border_color = 'rgba(255, 99, 132, 1)'

    dataset_label = ""
    pb_value = None

    is_cardio = exercise.category and 'cardio' in exercise.category.lower()

    if is_cardio:
        dataset_label = 'Distance (km)'
        valid_logs = [log for log in logs if log.distance_km is not None]
        if valid_logs:
            pb_value = max(log.distance_km for log in valid_logs)
        
        for log in logs:
            if log.distance_km is not None:
                chart_labels.append(log.date.strftime('%Y-%m-%d'))
                data_points.append(log.distance_km)
                if log.distance_km == pb_value:
                    point_radii.append(pb_point_radius)
                    point_background_colors.append(pb_point_bg_color)
                    point_border_colors.append(pb_point_border_color)
                else:
                    point_radii.append(default_point_radius)
                    point_background_colors.append(default_point_bg_color)
                    point_border_colors.append(default_point_border_color)
    else:
        dataset_label = 'Weight Lifted'
        valid_logs = [log for log in logs if log.weight is not None]
        if valid_logs:
            pb_value = max(log.weight for log in valid_logs)

        for log in logs:
            if log.weight is not None:
                chart_labels.append(log.date.strftime('%Y-%m-%d %H:%M'))
                data_points.append(log.weight)
                if log.weight == pb_value:
                    point_radii.append(pb_point_radius)
                    point_background_colors.append(pb_point_bg_color)
                    point_border_colors.append(pb_point_border_color)
                else:
                    point_radii.append(default_point_radius)
                    point_background_colors.append(default_point_bg_color)
                    point_border_colors.append(default_point_border_color)
    
    chart_data = {
        'labels': chart_labels,
        'datasets': []
    }

    if data_points:
        chart_data['datasets'].append({
            'label': dataset_label,
            'data': data_points,
            'fill': False,
            'borderColor': default_point_border_color,
            'tension': 0.1,
            'pointRadius': point_radii,
            'pointBackgroundColor': point_background_colors,
            'pointBorderColor': point_border_colors,
            'pointHoverRadius': [r + 2 for r in point_radii]
        })

    chart_data_json = json.dumps(chart_data)

    return render_template('exercise_progress.html',
                         title=f"{exercise.name} Progress",
                         exercise=exercise,
                         chart_data_json=chart_data_json) 