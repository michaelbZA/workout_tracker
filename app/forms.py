# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, FloatField, DateField
from wtforms.validators import DataRequired, Length, Optional, NumberRange # Optional allows empty fields if not DataRequired

class ExerciseForm(FlaskForm):
    name = StringField('Exercise Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description (Optional)',
                                validators=[Length(max=200)])
    category = SelectField('Category',
                          choices=[
                              ('chest', 'Chest'),
                              ('back', 'Back'),
                              ('shoulders', 'Shoulders'),
                              ('arms', 'Arms'),
                              ('legs', 'Legs'),
                              ('core', 'Core'),
                              ('cardio', 'Cardio'),
                              ('other', 'Other')
                          ],
                          validators=[DataRequired()])
    submit = SubmitField('Add Exercise')

class WorkoutLogForm(FlaskForm):
    # This field will be populated with choices from the database in the route
    exercise = SelectField('Exercise', coerce=int, validators=[DataRequired()])
    # We'll use the default date (today) in the route, but a DateField could be added if needed
    # date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    sets = IntegerField('Sets', validators=[Optional(), NumberRange(min=0)])
    reps = IntegerField('Reps (per set)', validators=[Optional(), NumberRange(min=0)])
    weight = FloatField('Weight (kg/lbs)', validators=[Optional(), NumberRange(min=0)])
    duration_minutes = IntegerField('Duration (minutes)', validators=[Optional(), NumberRange(min=0)])
    distance_km = FloatField('Distance (km)', validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField('Notes', validators=[Length(max=300)])
    submit = SubmitField('Log Workout')