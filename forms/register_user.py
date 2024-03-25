from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, IntegerField, DateField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    birth_date = DateField('Дата рождения', validators=[DataRequired()])
    email = EmailField('Электронная почта', validators=[DataRequired()])
    phone_number = StringField('Номер телефона', validators=[DataRequired()])
    submit = SubmitField('Регистрация')
