from flask import Blueprint, render_template, json
from flask_login import login_required, current_user
from app import db
from app.models import Exercise, WorkoutLog
from datetime import datetime, timedelta
from . import main_bp

@main_bp.route('/')
@main_bp.route('/index')
@login_required
def index():
    # Get all exercises for the current user
    exercises = Exercise.query.filter_by(user_id=current_user.id).order_by(Exercise.name).all()
    
    # Get personal bests for each exercise
    personal_bests = {}
    for exercise in exercises:
        if exercise.category == 'cardio':
            # For cardio, find the longest distance
            best_log = WorkoutLog.query.filter_by(
                exercise_id=exercise.id
            ).order_by(WorkoutLog.distance_km.desc()).first()
            
            if best_log and best_log.distance_km:
                personal_bests[exercise.id] = {
                    'value': best_log.distance_km,
                    'unit': 'km',
                    'date': best_log.date
                }
        else:
            # For strength exercises, find the heaviest weight
            best_log = WorkoutLog.query.filter_by(
                exercise_id=exercise.id
            ).order_by(WorkoutLog.weight.desc()).first()
            
            if best_log and best_log.weight:
                personal_bests[exercise.id] = {
                    'value': best_log.weight,
                    'unit': 'kg',
                    'date': best_log.date,
                    'reps': best_log.reps
                }
    
    # Group exercises by category
    exercises_by_category = {}
    for exercise in exercises:
        if exercise.category not in exercises_by_category:
            exercises_by_category[exercise.category] = []
        exercises_by_category[exercise.category].append(exercise)
    
    # Sort categories to show strength categories first, then cardio
    category_order = ['chest', 'back', 'shoulders', 'arms', 'legs', 'core', 'cardio', 'other']
    sorted_categories = sorted(exercises_by_category.keys(), 
                             key=lambda x: category_order.index(x) if x in category_order else len(category_order))
    
    # Get recent workout logs
    recent_logs = WorkoutLog.query.join(Exercise).filter(
        Exercise.user_id == current_user.id
    ).order_by(WorkoutLog.date.desc()).limit(5).all()
    
    # Get workout statistics
    total_workouts = WorkoutLog.query.join(Exercise).filter(
        Exercise.user_id == current_user.id
    ).count()
    
    # Calculate strength statistics
    strength_logs = WorkoutLog.query.join(Exercise).filter(
        Exercise.user_id == current_user.id,
        Exercise.category != 'cardio'
    ).all()
    
    total_sets = sum(log.sets or 0 for log in strength_logs)
    total_weight = sum(log.weight or 0 for log in strength_logs)
    strength_workouts = len([log for log in strength_logs if log.weight is not None])
    avg_weight = total_weight / strength_workouts if strength_workouts > 0 else 0
    
    # Find most common strength exercise
    exercise_counts = {}
    for log in strength_logs:
        if log.exercise.name not in exercise_counts:
            exercise_counts[log.exercise.name] = 0
        exercise_counts[log.exercise.name] += 1
    most_common_exercise = max(exercise_counts.items(), key=lambda x: x[1])[0] if exercise_counts else "None"
    
    # Calculate cardio statistics
    cardio_logs = WorkoutLog.query.join(Exercise).filter(
        Exercise.user_id == current_user.id,
        Exercise.category == 'cardio'
    ).all()
    
    total_distance = sum(log.distance_km or 0 for log in cardio_logs)
    total_duration = sum(log.duration_minutes or 0 for log in cardio_logs)
    cardio_workouts = len([log for log in cardio_logs if log.distance_km is not None])
    
    # Calculate average pace (minutes per km)
    avg_pace = total_duration / total_distance if total_distance > 0 else 0
    
    # Calculate average distance per session
    avg_distance = total_distance / cardio_workouts if cardio_workouts > 0 else 0
    
    # Prepare data for the e1RM chart
    strength_exercises = [e for e in exercises if e.category != 'cardio']
    strength_exercises_with_data = []
    strength_exercises_data = []
    
    for exercise in strength_exercises:
        best_log = WorkoutLog.query.filter_by(
            exercise_id=exercise.id
        ).order_by(WorkoutLog.weight.desc()).first()
        
        if best_log and best_log.weight and best_log.reps:
            # Calculate estimated 1RM
            estimated_1rm = best_log.weight * (1 + (best_log.reps / 30.0))
            strength_exercises_with_data.append(exercise)
            strength_exercises_data.append(estimated_1rm)
    
    pb_bar_chart_data = {
        'labels': [e.name for e in strength_exercises_with_data],
        'datasets': [{
            'label': 'Estimated 1RM (kg)',
            'data': strength_exercises_data,
            'backgroundColor': 'rgba(75, 192, 192, 0.6)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1
        }]
    }
    
    # Only show the chart if there are strength exercises with data
    if not strength_exercises_with_data:
        pb_bar_chart_data = None
    
    return render_template('index.html',
                         title='Home',
                         exercises=exercises,
                         exercises_by_category=exercises_by_category,
                         sorted_categories=sorted_categories,
                         personal_bests=personal_bests,
                         recent_logs=recent_logs,
                         total_workouts=total_workouts,
                         total_sets=total_sets,
                         avg_weight=avg_weight,
                         most_common_exercise=most_common_exercise,
                         total_distance=total_distance,
                         total_duration=total_duration,
                         avg_pace=avg_pace,
                         avg_distance=avg_distance,
                         pb_bar_chart_data_json=json.dumps(pb_bar_chart_data) if pb_bar_chart_data else None) 