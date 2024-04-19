from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, EmailField
from wtforms.validators import DataRequired


class OrderForm(FlaskForm):
    address = StringField('Адрес', validators=[DataRequired()])
    email = EmailField('Ваш e-mail, на него придут подробности заказ', validators=[DataRequired()])
    type_of_paid = SelectField('Тип оплаты', choices=[(1, 'Наличными'), (2, 'Картой через терминал курьера')])
    phone_number = StringField('Ваш номер телефона', validators=[DataRequired()])
    submit = SubmitField('Подтвердить заказ')
