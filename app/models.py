# app/models.py
from app import db # Import the db instance from app/__init__.py
from datetime import datetime, timezone # For setting default timestamps

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(50), nullable=True) # e.g., Chest, Legs, Cardio

    # Relationship: An exercise can have many workout logs
    # backref='exercise' adds an 'exercise' attribute to WorkoutLog instances
    # lazy=True means SQLAlchemy will load the related objects as needed
    workout_logs = db.relationship('WorkoutLog', backref='exercise', lazy=True)

    def __repr__(self):
        return f"<Exercise {self.name}>"

class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True) # For weightlifting
    duration_minutes = db.Column(db.Integer, nullable=True) # For cardio/timed exercises
    distance_km = db.Column(db.Float, nullable=True) # For cardio like running/cycling
    notes = db.Column(db.String(300), nullable=True)
    is_pb = db.Column(db.Boolean, default=False) # You might calculate this dynamically later

    def __repr__(self):
        return f"<WorkoutLog {self.id} for Exercise {self.exercise_id} on {self.date}>"