from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, IntegerField, SelectField, FileField
from wtforms.validators import DataRequired


class PositionForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    weight = IntegerField('Вес', validators=[DataRequired()])
    price = IntegerField('Стоимость', validators=[DataRequired()])
    structure = StringField('Состав', validators=[DataRequired()])
    type = SelectField('Категория', choices=[(0, 'Роллы'), (1, 'Пицца'), (2, 'Наборы'), (3, 'Салаты и Закуски')])
    image = FileField('Изображение', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Добавить позицию')

