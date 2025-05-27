from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models import WorkoutLog, Exercise
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta
from collections import defaultdict

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
@login_required
def analytics_dashboard():
    return render_template('analytics/dashboard.html')

@analytics_bp.route('/api/analytics/strength-progress')
@login_required
def strength_progress():
    # Get the last 30 days of strength workouts
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # List of strength-related categories
    strength_categories = ['arms', 'chest', 'back', 'legs', 'shoulders', 'core']
    
    # Query for strength exercises
    strength_logs = WorkoutLog.query.join(Exercise).filter(
        WorkoutLog.user_id == current_user.id,
        Exercise.category.in_(strength_categories),
        WorkoutLog.date >= thirty_days_ago
    ).order_by(WorkoutLog.date).all()
    
    # Organize data by exercise and date
    progress_data = defaultdict(lambda: defaultdict(list))
    for log in strength_logs:
        date_str = log.date.strftime('%Y-%m-%d')
        progress_data[log.exercise.name][date_str].append({
            'weight': log.weight,
            'reps': log.reps,
            'sets': log.sets
        })
    
    return jsonify(progress_data)

@analytics_bp.route('/api/analytics/cardio-progress')
@login_required
def cardio_progress():
    # Get the last 30 days of cardio workouts
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Query for cardio exercises
    cardio_logs = WorkoutLog.query.join(Exercise).filter(
        WorkoutLog.user_id == current_user.id,
        Exercise.category == 'cardio',
        WorkoutLog.date >= thirty_days_ago
    ).order_by(WorkoutLog.date).all()
    
    # Organize data by exercise and date
    progress_data = defaultdict(lambda: defaultdict(list))
    for log in cardio_logs:
        date_str = log.date.strftime('%Y-%m-%d')
        progress_data[log.exercise.name][date_str].append({
            'duration': log.duration_minutes,
            'distance': log.distance_km
        })
    
    return jsonify(progress_data)

@analytics_bp.route('/api/analytics/personal-records')
@login_required
def personal_records():
    # Get all personal bests and records
    records = WorkoutLog.query.filter(
        WorkoutLog.user_id == current_user.id,
        (WorkoutLog.is_pb == True) | (WorkoutLog.is_pr == True)
    ).order_by(WorkoutLog.date.desc()).all()
    
    pr_data = []
    for record in records:
        pr_data.append({
            'exercise': record.exercise.name,
            'date': record.date.strftime('%Y-%m-%d'),
            'weight': record.weight,
            'reps': record.reps,
            'sets': record.sets,
            'duration': record.duration_minutes,
            'distance': record.distance_km,
            'is_pb': record.is_pb,
            'is_pr': record.is_pr,
            'pr_description': record.pr_description
        })
    
    return jsonify(pr_data)

@analytics_bp.route('/api/analytics/workout-stats')
@login_required
def workout_stats():
    # Get workout frequency and volume stats
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # List of strength-related categories
    strength_categories = ['arms', 'chest', 'back', 'legs', 'shoulders', 'core']
    
    # Total workouts in last 30 days
    total_workouts = WorkoutLog.query.filter(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.date >= thirty_days_ago
    ).count()
    
    # Total volume (weight × reps × sets) for strength exercises
    strength_volume = db.session.query(
        func.sum(WorkoutLog.weight * WorkoutLog.reps * WorkoutLog.sets)
    ).join(Exercise).filter(
        WorkoutLog.user_id == current_user.id,
        Exercise.category.in_(strength_categories),
        WorkoutLog.date >= thirty_days_ago
    ).scalar() or 0
    
    # Total cardio minutes
    cardio_minutes = db.session.query(
        func.sum(WorkoutLog.duration_minutes)
    ).join(Exercise).filter(
        WorkoutLog.user_id == current_user.id,
        Exercise.category == 'cardio',
        WorkoutLog.date >= thirty_days_ago
    ).scalar() or 0
    
    return jsonify({
        'total_workouts': total_workouts,
        'strength_volume': strength_volume,
        'cardio_minutes': cardio_minutes
    }) 