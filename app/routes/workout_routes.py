from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Exercise, WorkoutLog, WorkoutPlan, PlannedExercise
from app.forms import WorkoutLogForm, WorkoutPlanForm, PlannedExerciseForm
from datetime import datetime, timedelta
from sqlalchemy import and_, func
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

@workout.route('/plans')
@login_required
def workout_plans():
    plans = WorkoutPlan.query.filter_by(user_id=current_user.id).order_by(WorkoutPlan.created_at.desc()).all()
    return render_template('workout/plans.html', plans=plans)

@workout.route('/templates')
@login_required
def templates():
    """View all workout templates"""
    templates = WorkoutPlan.query.filter_by(
        user_id=current_user.id,
        is_template=True
    ).order_by(WorkoutPlan.name).all()
    return render_template('workout_templates.html', title='Workout Templates', templates=templates)

@workout.route('/templates/<int:template_id>/use', methods=['POST'])
@login_required
def use_template(template_id):
    """Create a new workout plan from a template"""
    template = WorkoutPlan.query.filter_by(
        id=template_id,
        user_id=current_user.id,
        is_template=True
    ).first_or_404()
    
    # Create new plan from template
    new_plan = template.create_from_template(template)
    db.session.add(new_plan)
    db.session.commit()
    
    flash('New workout plan created from template!', 'success')
    return redirect(url_for('workout.view_plan', plan_id=new_plan.id))

@workout.route('/plans/create', methods=['GET', 'POST'])
@login_required
def create_plan():
    """Create a new workout plan or template"""
    form = WorkoutPlanForm()
    
    if form.validate_on_submit():
        plan = WorkoutPlan(
            name=form.name.data,
            description=form.description.data,
            user_id=current_user.id,
            is_template=form.is_template.data,
            template_category=form.template_category.data if form.is_template.data else None,
            difficulty_level=form.difficulty_level.data,
            estimated_duration=form.estimated_duration.data,
            equipment_needed=form.equipment_needed.data,
            target_muscle_groups=form.target_muscle_groups.data,
            notes=form.notes.data
        )
        
        db.session.add(plan)
        db.session.commit()
        
        if form.is_template.data:
            flash('Workout template created successfully!', 'success')
            return redirect(url_for('workout.templates'))
        else:
            flash('Workout plan created successfully!', 'success')
            return redirect(url_for('workout.view_plan', plan_id=plan.id))
    
    return render_template('create_plan.html', title='Create Workout Plan', form=form)

@workout.route('/plans/<int:plan_id>')
@login_required
def view_workout_plan(plan_id):
    plan = WorkoutPlan.query.get_or_404(plan_id)
    if plan.user_id != current_user.id:
        abort(403)
    return render_template('workout/view_plan.html', plan=plan, PlannedExercise=PlannedExercise)

@workout.route('/plans/<int:plan_id>/add-exercise', methods=['GET', 'POST'])
@login_required
def add_planned_exercise(plan_id):
    plan = WorkoutPlan.query.get_or_404(plan_id)
    if plan.user_id != current_user.id:
        abort(403)
    
    form = PlannedExerciseForm()
    form.exercise.choices = [(e.id, e.name) for e in Exercise.query.filter_by(user_id=current_user.id).all()]
    
    if form.validate_on_submit():
        exercise = PlannedExercise(
            workout_plan_id=plan_id,
            exercise_id=form.exercise.data,
            target_sets=form.target_sets.data,
            target_reps=form.target_reps.data,
            target_weight=form.target_weight.data,
            target_duration=form.target_duration.data,
            target_distance=form.target_distance.data,
            order=form.order.data,
            notes=form.notes.data
        )
        db.session.add(exercise)
        db.session.commit()
        flash('Exercise added to plan!', 'success')
        return redirect(url_for('workout.view_workout_plan', plan_id=plan_id))
    
    return render_template('workout/add_exercise.html', form=form, plan=plan)

@workout.route('/plans/<int:plan_id>/delete', methods=['POST'])
@login_required
def delete_workout_plan(plan_id):
    plan = WorkoutPlan.query.get_or_404(plan_id)
    if plan.user_id != current_user.id:
        abort(403)
    db.session.delete(plan)
    db.session.commit()
    flash('Workout plan deleted.', 'success')
    return redirect(url_for('workout.workout_plans'))

@workout.route('/plans/<int:plan_id>/exercise/<int:exercise_id>/delete', methods=['POST'])
@login_required
def delete_planned_exercise(plan_id, exercise_id):
    exercise = PlannedExercise.query.get_or_404(exercise_id)
    if exercise.workout_plan.user_id != current_user.id:
        abort(403)
    db.session.delete(exercise)
    db.session.commit()
    flash('Exercise removed from plan.', 'success')
    return redirect(url_for('workout.view_workout_plan', plan_id=plan_id))

@workout.route('/plans/<int:plan_id>/exercise/<int:exercise_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_planned_exercise(plan_id, exercise_id):
    plan = WorkoutPlan.query.get_or_404(plan_id)
    if plan.user_id != current_user.id:
        abort(403)
    
    planned_exercise = PlannedExercise.query.get_or_404(exercise_id)
    if planned_exercise.workout_plan_id != plan_id:
        abort(404)
    
    form = PlannedExerciseForm()
    form.exercise.choices = [(e.id, e.name) for e in Exercise.query.filter_by(user_id=current_user.id).all()]
    
    if request.method == 'GET':
        form.exercise.data = planned_exercise.exercise_id
        form.target_sets.data = planned_exercise.target_sets
        form.target_reps.data = planned_exercise.target_reps
        form.target_weight.data = planned_exercise.target_weight
        form.target_duration.data = planned_exercise.target_duration
        form.target_distance.data = planned_exercise.target_distance
        form.order.data = planned_exercise.order
        form.notes.data = planned_exercise.notes
    
    if form.validate_on_submit():
        planned_exercise.exercise_id = form.exercise.data
        planned_exercise.target_sets = form.target_sets.data
        planned_exercise.target_reps = form.target_reps.data
        planned_exercise.target_weight = form.target_weight.data
        planned_exercise.target_duration = form.target_duration.data
        planned_exercise.target_distance = form.target_distance.data
        planned_exercise.order = form.order.data
        planned_exercise.notes = form.notes.data
        
        db.session.commit()
        flash('Exercise updated in plan!', 'success')
        return redirect(url_for('workout.view_workout_plan', plan_id=plan_id))
    
    return render_template('workout/edit_exercise.html', form=form, plan=plan, planned_exercise=planned_exercise)

@workout.route('/plans/<int:plan_id>/exercise/<int:exercise_id>/log', methods=['GET', 'POST'])
@login_required
def log_from_plan(plan_id, exercise_id):
    try:
        plan = WorkoutPlan.query.get_or_404(plan_id)
        if plan.user_id != current_user.id:
            abort(403)
        
        planned_exercise = PlannedExercise.query.get_or_404(exercise_id)
        if planned_exercise.workout_plan_id != plan_id:
            abort(404)
        
        # Get the exercise from the planned exercise
        exercise = Exercise.query.get(planned_exercise.exercise_id)
        if not exercise:
            print(f"Exercise not found for ID: {planned_exercise.exercise_id}")  # Debug log
            flash('Exercise not found.', 'error')
            return redirect(url_for('workout.view_workout_plan', plan_id=plan_id))
        
        print(f"Found exercise: {exercise.name} (ID: {exercise.id})")  # Debug log
        
        form = WorkoutLogForm()
        form.exercise.choices = [(e.id, e.name) for e in Exercise.query.filter_by(user_id=current_user.id).order_by(Exercise.name).all()]
        
        if request.method == 'GET':
            # Only pre-fill the form with target values on GET request
            form.exercise.data = planned_exercise.exercise_id
            form.sets.data = planned_exercise.target_sets
            form.reps.data = planned_exercise.target_reps
            form.weight.data = planned_exercise.target_weight
            form.duration_minutes.data = planned_exercise.target_duration
            form.distance_km.data = planned_exercise.target_distance
            form.notes.data = planned_exercise.notes
        
        if form.validate_on_submit():
            print("Form validated successfully")  # Debug log
            print(f"Form data: exercise_id={form.exercise.data}, sets={form.sets.data}, reps={form.reps.data}, weight={form.weight.data}")  # Debug log
            
            # Get the exercise again to ensure it exists
            exercise = Exercise.query.get(form.exercise.data)
            if not exercise:
                print(f"Exercise not found for ID: {form.exercise.data}")  # Debug log
                flash('Selected exercise not found.', 'error')
                return render_template('log_workout.html', 
                                    title='Log Workout',
                                    form=form,
                                    from_plan=True,
                                    plan_name=plan.name)
            
            print(f"Found exercise for form submission: {exercise.name} (ID: {exercise.id})")  # Debug log
            
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
            
            try:
                # Validate required fields based on exercise type
                if exercise.category in ['arms', 'chest', 'back', 'legs', 'shoulders', 'core']:
                    if not form.sets.data or not form.reps.data or not form.weight.data:
                        flash('For strength exercises, please fill in sets, reps, and weight.', 'error')
                        return render_template('log_workout.html', 
                                            title='Log Workout',
                                            form=form,
                                            from_plan=True,
                                            plan_name=plan.name)
                elif exercise.category == 'cardio':
                    if not form.duration_minutes.data and not form.distance_km.data:
                        flash('For cardio exercises, please fill in either duration or distance.', 'error')
                        return render_template('log_workout.html', 
                                            title='Log Workout',
                                            form=form,
                                            from_plan=True,
                                            plan_name=plan.name)

                workout_log = WorkoutLog(
                    exercise_id=form.exercise.data,
                    user_id=current_user.id,
                    date=datetime.utcnow(),
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
                
                print(f"Created workout log object: {workout_log}")  # Debug log
                
                db.session.add(workout_log)
                db.session.commit()
                
                print("Workout log committed to database")  # Debug log
                
                if is_pb:
                    flash('New personal best achieved!', 'success')
                if is_pr:
                    flash('New personal record logged!', 'success')
                if not is_pb and not is_pr:
                    flash('Workout logged successfully!', 'success')
                return redirect(url_for('workout.history'))
            except Exception as e:
                print(f"Error saving workout log: {str(e)}")  # Debug log
                db.session.rollback()
                flash(f'Error saving workout log: {str(e)}', 'error')
        else:
            print(f"Form validation failed: {form.errors}")  # Debug log
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'error')
        
        return render_template('log_workout.html', 
                             title='Log Workout',
                             form=form,
                             from_plan=True,
                             plan_name=plan.name)
    except Exception as e:
        print(f"Unexpected error in log_from_plan: {str(e)}")  # Debug log
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('workout.view_workout_plan', plan_id=plan_id)) 

@workout.route('/plans/<int:plan_id>/copy', methods=['POST'])
@login_required
def copy_workout_plan(plan_id):
    original_plan = WorkoutPlan.query.get_or_404(plan_id)
    if original_plan.user_id != current_user.id:
        abort(403)
    
    # Create a new plan with the same name and description
    new_plan = WorkoutPlan(
        name=f"{original_plan.name} (Copy)",
        description=original_plan.description,
        user_id=current_user.id
    )
    db.session.add(new_plan)
    db.session.flush()  # Get the new plan's ID
    
    # Copy all exercises from the original plan
    for exercise in original_plan.planned_exercises:
        new_exercise = PlannedExercise(
            workout_plan_id=new_plan.id,
            exercise_id=exercise.exercise_id,
            target_sets=exercise.target_sets,
            target_reps=exercise.target_reps,
            target_weight=exercise.target_weight,
            target_duration=exercise.target_duration,
            target_distance=exercise.target_distance,
            order=exercise.order,
            notes=exercise.notes
        )
        db.session.add(new_exercise)
    
    db.session.commit()
    flash('Workout plan copied successfully!', 'success')
    return redirect(url_for('workout.view_workout_plan', plan_id=new_plan.id)) 

@workout.route('/plans/<int:plan_id>/toggle-active', methods=['POST'])
@login_required
def toggle_plan_active(plan_id):
    plan = WorkoutPlan.query.get_or_404(plan_id)
    if plan.user_id != current_user.id:
        abort(403)
    
    # If this plan is being activated, deactivate all other plans
    if not plan.is_active:
        WorkoutPlan.query.filter_by(user_id=current_user.id).update({WorkoutPlan.is_active: False})
    
    plan.is_active = not plan.is_active
    db.session.commit()
    
    status = "activated" if plan.is_active else "deactivated"
    flash(f'Workout plan {status}!', 'success')
    return redirect(url_for('workout.view_workout_plan', plan_id=plan_id)) 

@workout.route('/plans/<int:plan_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_workout_plan(plan_id):
    plan = WorkoutPlan.query.get_or_404(plan_id)
    if plan.user_id != current_user.id:
        abort(403)
    
    form = WorkoutPlanForm()
    if request.method == 'GET':
        form.name.data = plan.name
        form.description.data = plan.description
    
    if form.validate_on_submit():
        plan.name = form.name.data
        plan.description = form.description.data
        db.session.commit()
        flash('Workout plan updated successfully!', 'success')
        return redirect(url_for('workout.view_workout_plan', plan_id=plan_id))
    
    return render_template('workout/edit_plan.html', form=form, plan=plan)

@workout.route('/dashboard')
@login_required
def dashboard():
    # Get user's workout data
    user_id = current_user.id
    
    # Get total workouts
    total_workouts = WorkoutLog.query.filter_by(user_id=user_id).count()
    
    # Get workouts this month
    from datetime import datetime, timedelta
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    workouts_this_month = WorkoutLog.query.filter(
        WorkoutLog.user_id == user_id,
        WorkoutLog.date >= first_day_of_month
    ).count()
    
    # Get personal records
    personal_records = WorkoutLog.query.filter_by(
        user_id=user_id,
        is_pb=True
    ).order_by(WorkoutLog.date.desc()).limit(5).all()
    
    # Get recent workouts
    recent_workouts = WorkoutLog.query.filter_by(
        user_id=user_id
    ).order_by(WorkoutLog.date.desc()).limit(5).all()
    
    # Get workout frequency by day of week
    workout_frequency = db.session.query(
        func.extract('dow', WorkoutLog.date).label('day_of_week'),
        func.count(WorkoutLog.id).label('count')
    ).filter(
        WorkoutLog.user_id == user_id
    ).group_by('day_of_week').all()
    
    # Get exercise distribution by category
    exercise_distribution = db.session.query(
        Exercise.category,
        func.count(WorkoutLog.id).label('count')
    ).join(
        WorkoutLog,
        WorkoutLog.exercise_id == Exercise.id
    ).filter(
        WorkoutLog.user_id == user_id
    ).group_by(Exercise.category).all()
    
    # Get active workout plan
    active_plan = WorkoutPlan.query.filter_by(
        user_id=user_id,
        is_active=True
    ).first()
    
    # Get workout trend (last 7 days)
    last_7_days = datetime.utcnow() - timedelta(days=7)
    workout_trend = db.session.query(
        func.strftime('%Y-%m-%d', WorkoutLog.date).label('date'),
        func.count(WorkoutLog.id).label('count')
    ).filter(
        WorkoutLog.user_id == user_id,
        WorkoutLog.date >= last_7_days
    ).group_by('date').order_by('date').all()
    
    # Get total volume (weight × reps × sets) for strength exercises
    total_volume = db.session.query(
        func.sum(WorkoutLog.weight * WorkoutLog.reps * WorkoutLog.sets)
    ).join(
        Exercise,
        WorkoutLog.exercise_id == Exercise.id
    ).filter(
        WorkoutLog.user_id == user_id,
        Exercise.category.in_(['arms', 'chest', 'back', 'legs', 'shoulders', 'core'])
    ).scalar() or 0
    
    return render_template('workout/dashboard.html',
                         title='Dashboard',
                         total_workouts=total_workouts,
                         workouts_this_month=workouts_this_month,
                         personal_records=personal_records,
                         recent_workouts=recent_workouts,
                         workout_frequency=workout_frequency,
                         exercise_distribution=exercise_distribution,
                         active_plan=active_plan,
                         workout_trend=workout_trend,
                         total_volume=total_volume) 