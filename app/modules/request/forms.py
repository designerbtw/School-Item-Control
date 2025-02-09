from flask_wtf import FlaskForm

from wtforms import SubmitField, IntegerField
from wtforms.validators import DataRequired


class CreateRequestForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Change')