# app/models.py
from app import db, login_manager
from datetime import datetime, timezone # For setting default timestamps
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    exercises = db.relationship('Exercise', backref='user', lazy='dynamic')
    workout_logs = db.relationship('WorkoutLog', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)  # Main category (e.g., 'strength' or 'cardio')
    subcategory = db.Column(db.String(50))  # Subcategory (e.g., 'chest', 'back', etc.)
    form_instructions = db.Column(db.Text)  # Detailed form instructions
    equipment_needed = db.Column(db.String(200))  # Required equipment
    difficulty_level = db.Column(db.String(20))  # Beginner, Intermediate, Advanced
    is_favorite = db.Column(db.Boolean, default=False)  # Favorite status
    gif_url = db.Column(db.String(500))  # URL to exercise demonstration GIF
    common_notes = db.Column(db.Text)  # Common mistakes and tips
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)  # Track when the exercise was last used
    
    workout_logs = db.relationship('WorkoutLog', backref='exercise', lazy='dynamic')

    def __repr__(self):
        return f'<Exercise {self.name}>'

class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Float)  # in kg
    duration_minutes = db.Column(db.Integer)  # for cardio exercises
    distance_km = db.Column(db.Float)  # for cardio exercises
    notes = db.Column(db.Text)
    is_pb = db.Column(db.Boolean, default=False)  # Personal Best
    is_pr = db.Column(db.Boolean, default=False)  # Personal Record
    pr_description = db.Column(db.Text)  # Description of the PR achievement

    def __repr__(self):
        exercise_name = self.exercise.name if self.exercise else f"Exercise {self.exercise_id}"
        return f'<WorkoutLog {exercise_name} {self.date}>'

class WorkoutPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref='workout_plans')
    planned_exercises = db.relationship('PlannedExercise', backref='workout_plan', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<WorkoutPlan {self.name}>'

class PlannedExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_plan_id = db.Column(db.Integer, db.ForeignKey('workout_plan.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    target_sets = db.Column(db.Integer)
    target_reps = db.Column(db.Integer)
    target_weight = db.Column(db.Float)  # in kg
    target_duration = db.Column(db.Integer)  # in minutes
    target_distance = db.Column(db.Float)  # in km
    order = db.Column(db.Integer)  # For ordering exercises in the plan
    notes = db.Column(db.Text)
    
    # Relationships
    exercise = db.relationship('Exercise')
    
    def __repr__(self):
        return f'<PlannedExercise {self.exercise.name} in {self.workout_plan.name}>'