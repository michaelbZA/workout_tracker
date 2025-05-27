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
    category = db.Column(db.String(50), nullable=False)  # 'strength' or 'cardio'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
        return f'<WorkoutLog {self.exercise.name} {self.date}>'