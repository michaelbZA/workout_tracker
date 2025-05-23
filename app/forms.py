# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class ExerciseForm(FlaskForm):
    name = StringField('Exercise Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description (Optional)',
                                validators=[Length(max=200)])
    category = StringField('Category (e.g., Chest, Legs, Cardio)',
                           validators=[Length(max=50)])
    submit = SubmitField('Add Exercise')