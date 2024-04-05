import datetime
import json
import os

from flask import Flask, render_template, redirect, make_response, request, session, abort, flash
from werkzeug.utils import secure_filename

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import jsonify, make_response
from werkzeug.exceptions import RequestEntityTooLarge

from data import db_session
from data.users import User
from data.tools import check_phone_number
from data.dishes import Dish
from data.types import Type
from forms.register_user import RegisterForm
from forms.login_form import LoginForm
from forms.new_position_form import PositionForm

from data.consts import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'upload/img'

login_manager = LoginManager()
login_manager.init_app(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def main():
    db_session.global_init("db/database.db")
    app.run(debug=True)


@app.route('/new_position', methods=['GET', 'POST'])
@login_required
def create_position():
    if current_user.is_authenticated and current_user.status == "super":
        form = PositionForm()
        if form.validate_on_submit():
            if 'image' not in request.files:
                flash('Файл не был загружен.')
                return redirect(request.url)
            file = request.files['image']
            if file:
                try:
                    if file.filename == '':
                        flash('Файл не выбран.')
                        return redirect(request.url)
                    if file and allowed_file(file.filename):
                        pass  # TODO: Сделать загрузку фотографий на сервер, зацепить их во всех базах данных

                    db_sess = db_session.create_session()
                    dish = Dish()
                    dish.title = form.title.data
                    dish.description = form.description.data
                    dish.weight = form.weight.data
                    dish.price = form.price.data
                    dish.structure = form.structure.data
                    dish.type = db_sess.query(Type).filter(Type.id == int(form.type.data)).first()
                    db_sess.add(dish)
                    db_sess.commit()
                except RequestEntityTooLarge:
                    flash('Загружаемый файл слишком большой.')
            return render_template('static_templates/order_added.html')
        return render_template('new_position.html', form=form)
    else:
        return redirect('/')


@app.route('/active_orders')
@login_required
def active_orders():  # TODO: Сделать форму, нормальную загрузку фотографий
    if current_user.is_authenticated and current_user.status == "super":
        return render_template('active_orders.html')
    else:
        return redirect('/')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.phone_number == check_phone_number(form.phone_number.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный номер телефона или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/')
@app.route('/index')
def index():
    # return redirect('/register')
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с такой почтой уже есть")
        if db_sess.query(User).filter(User.phone_number == form.phone_number.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким номером телефона уже есть")
        if not check_phone_number(form.phone_number.data):
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Некорректный номер телефона")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data,
            birth_date=form.birth_date.data,
            phone_number=check_phone_number(form.phone_number.data)
        )

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()
