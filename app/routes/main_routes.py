from flask import Blueprint, render_template, json
from flask_login import login_required, current_user
from app import db
from app.models import Exercise, WorkoutLog
from datetime import datetime, timedelta
from . import main_bp

@main_bp.route('/')
@login_required
def index():
    # Get recent workouts
    recent_workouts = WorkoutLog.query.filter_by(user_id=current_user.id).order_by(WorkoutLog.date.desc()).limit(5).all()
    
    # Get exercise stats
    total_exercises = Exercise.query.filter_by(user_id=current_user.id).count()
    total_workouts = WorkoutLog.query.filter_by(user_id=current_user.id).count()
    
    # Get personal bests
    personal_bests = WorkoutLog.query.filter_by(user_id=current_user.id, is_pb=True).order_by(WorkoutLog.date.desc()).limit(5).all()
    
    # Get workout frequency
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    workouts_last_30_days = WorkoutLog.query.filter(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.date >= thirty_days_ago
    ).count()

    exercises = Exercise.query.order_by(Exercise.name).all()
    workout_logs = WorkoutLog.query.join(Exercise).order_by(WorkoutLog.date.desc()).all()

    personal_bests_for_bar_chart = {}
    # Data for PB Comparison Bar Chart
    pb_bar_chart_labels = []  # Exercise names
    pb_bar_chart_e1rms = []   # e1RM values

    for ex in exercises:
        pb_data = {}
        e1rm_value_for_bar_chart = None # Variable to hold e1RM if calculated

        # Max Weight PB & Estimated 1RM
        max_weight_log = WorkoutLog.query.filter(
                                WorkoutLog.exercise_id == ex.id,
                                WorkoutLog.weight.isnot(None)
                            ).order_by(WorkoutLog.weight.desc(), WorkoutLog.date.desc()).first()
        
        if max_weight_log:
            pb_data['max_weight'] = {
                'value': max_weight_log.weight,
                'date': max_weight_log.date,
                'reps': max_weight_log.reps,
                'sets': max_weight_log.sets
            }
            if max_weight_log.reps and max_weight_log.reps > 0:
                weight = float(max_weight_log.weight)
                reps = int(max_weight_log.reps)
                if reps == 1:
                    e1rm = weight
                else:
                    e1rm = weight * (1 + (reps / 30.0))
                pb_data['e1rm'] = round(e1rm, 2)
                e1rm_value_for_bar_chart = round(e1rm, 2) # Store for bar chart

        # Longest Distance PB
        is_cardio = ex.category and 'cardio' in ex.category.lower()
        if is_cardio:
            max_distance_log = WorkoutLog.query.filter(
                                    WorkoutLog.exercise_id == ex.id,
                                    WorkoutLog.distance_km.isnot(None)
                                ).order_by(WorkoutLog.distance_km.desc(), WorkoutLog.date.desc()).first()
            if max_distance_log:
                pb_data['max_distance'] = {
                    'value': max_distance_log.distance_km,
                    'date': max_distance_log.date,
                    'duration': max_distance_log.duration_minutes
                }
        
        if pb_data:
            personal_bests_for_bar_chart[ex.id] = pb_data
            # If it's not a cardio exercise and has an e1RM, add it to our bar chart lists
            if not is_cardio and e1rm_value_for_bar_chart is not None:
                pb_bar_chart_labels.append(ex.name)
                pb_bar_chart_e1rms.append(e1rm_value_for_bar_chart)

    # Prepare data structure for Chart.js bar chart
    pb_bar_chart_data = {
        'labels': pb_bar_chart_labels,
        'datasets': [{
            'label': 'Estimated 1RM',
            'data': pb_bar_chart_e1rms,
            'backgroundColor': [
                'rgba(255, 99, 132, 0.5)',
                'rgba(54, 162, 235, 0.5)',
                'rgba(255, 206, 86, 0.5)',
                'rgba(75, 192, 192, 0.5)',
                'rgba(153, 102, 255, 0.5)',
                'rgba(255, 159, 64, 0.5)'
            ],
            'borderColor': [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            'borderWidth': 1
        }]
    }
    pb_bar_chart_data_json = json.dumps(pb_bar_chart_data)

    return render_template('index.html',
                         title='Dashboard',
                         recent_workouts=recent_workouts,
                         total_exercises=total_exercises,
                         total_workouts=total_workouts,
                         personal_bests=personal_bests,
                         workouts_last_30_days=workouts_last_30_days,
                         personal_bests_for_bar_chart=personal_bests_for_bar_chart,
                         pb_bar_chart_data_json=pb_bar_chart_data_json) 