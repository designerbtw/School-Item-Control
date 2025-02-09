from flask_wtf import FlaskForm

from wtforms import SubmitField, StringField, IntegerField, SelectField
from wtforms.validators import DataRequired

from app.models import ItemState

class CreateItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Create')


class ChangeItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    state = SelectField(
        "Состояние",
        choices=[
            (ItemState.NEW.value, "Новый"),
            (ItemState.USED.value, "Используемый"),
            (ItemState.BROKEN.value, "Сломан"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField('Change')


class AssignItemForm(FlaskForm):
    user_id = SelectField('Назначить пользователю')
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Назначить')