# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, FloatField, DateField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, NumberRange # Optional allows empty fields if not DataRequired

class ExerciseForm(FlaskForm):
    name = StringField('Exercise Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description',
                              validators=[Length(max=500)],
                              render_kw={"placeholder": "Brief description of the exercise"})
    category = SelectField('Main Category',
                          choices=[
                              ('strength', 'Strength Training'),
                              ('cardio', 'Cardio'),
                              ('flexibility', 'Flexibility'),
                              ('other', 'Other')
                          ],
                          validators=[DataRequired()])
    subcategory = SelectField('Subcategory',
                            choices=[
                                ('chest', 'Chest'),
                                ('back', 'Back'),
                                ('shoulders', 'Shoulders'),
                                ('arms', 'Arms'),
                                ('legs', 'Legs'),
                                ('core', 'Core'),
                                ('full_body', 'Full Body'),
                                ('running', 'Running'),
                                ('cycling', 'Cycling'),
                                ('swimming', 'Swimming'),
                                ('yoga', 'Yoga'),
                                ('stretching', 'Stretching'),
                                ('other', 'Other')
                            ],
                            validators=[DataRequired()])
    form_instructions = TextAreaField('Form Instructions',
                                    validators=[Length(max=1000)],
                                    render_kw={"placeholder": "Detailed instructions for proper form"})
    equipment_needed = StringField('Equipment Needed',
                                 validators=[Length(max=200)],
                                 render_kw={"placeholder": "e.g., Dumbbells, Bench, Resistance Bands"})
    difficulty_level = SelectField('Difficulty Level',
                                 choices=[
                                     ('beginner', 'Beginner'),
                                     ('intermediate', 'Intermediate'),
                                     ('advanced', 'Advanced')
                                 ],
                                 validators=[DataRequired()])
    gif_url = StringField('Exercise GIF URL',
                         validators=[Length(max=500), Optional()],
                         render_kw={"placeholder": "URL to exercise demonstration GIF"})
    common_notes = TextAreaField('Common Mistakes & Tips',
                               validators=[Length(max=1000), Optional()],
                               render_kw={"placeholder": "Common mistakes to avoid and helpful tips"})
    is_favorite = BooleanField('Mark as Favorite')
    submit = SubmitField('Save Exercise')

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
    is_pr = BooleanField('Mark as Personal Record (Other Achievement)')
    pr_description = TextAreaField('PR Description (Optional)', validators=[Length(max=200)])
    submit = SubmitField('Log Workout')

class WorkoutPlanForm(FlaskForm):
    name = StringField('Plan Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    is_template = BooleanField('Save as Template')
    template_category = SelectField('Template Category',
                                  choices=[
                                      ('full_body', 'Full Body'),
                                      ('upper_body', 'Upper Body'),
                                      ('lower_body', 'Lower Body'),
                                      ('push', 'Push'),
                                      ('pull', 'Pull'),
                                      ('cardio', 'Cardio'),
                                      ('hiit', 'HIIT'),
                                      ('strength', 'Strength'),
                                      ('flexibility', 'Flexibility'),
                                      ('other', 'Other')
                                  ])
    difficulty_level = SelectField('Difficulty Level',
                                 choices=[
                                     ('beginner', 'Beginner'),
                                     ('intermediate', 'Intermediate'),
                                     ('advanced', 'Advanced')
                                 ])
    estimated_duration = IntegerField('Estimated Duration (minutes)',
                                    validators=[Optional(), NumberRange(min=0)])
    equipment_needed = StringField('Equipment Needed',
                                 validators=[Length(max=200)],
                                 render_kw={"placeholder": "e.g., Dumbbells, Bench, Resistance Bands"})
    target_muscle_groups = StringField('Target Muscle Groups',
                                     validators=[Length(max=200)],
                                     render_kw={"placeholder": "e.g., Chest, Back, Legs"})
    notes = TextAreaField('Additional Notes')
    submit = SubmitField('Create Plan')

class PlannedExerciseForm(FlaskForm):
    exercise = SelectField('Exercise', coerce=int, validators=[DataRequired()])
    target_sets = IntegerField('Target Sets')
    target_reps = IntegerField('Target Reps')
    target_weight = FloatField('Target Weight (kg)')
    target_duration = IntegerField('Target Duration (minutes)')
    target_distance = FloatField('Target Distance (km)')
    order = IntegerField('Order in Plan')
    notes = TextAreaField('Notes')
    submit = SubmitField('Add Exercise')