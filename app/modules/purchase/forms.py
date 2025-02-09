from flask_wtf import FlaskForm

from wtforms import SubmitField, StringField, IntegerField
from wtforms.validators import DataRequired


class CreatePurchaseForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    supplier = StringField('Supplier', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    submit = SubmitField('Create')