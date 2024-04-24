import datetime
import json
import os

from flask import Flask, render_template, redirect, request, session, flash, current_app, jsonify, make_response, \
    url_for
from sqlalchemy.orm import joinedload
from flask_restful import Api

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.exceptions import RequestEntityTooLarge

from data import db_session
from api import dishes_resources

from data.users import User
from data.tools import check_phone_number, search_object, AddressError
from data.dishes import Dish
from data.types import Type
from data.images import Image
from data.orders import Order
from data.order_details import Detail

from forms.register_user import RegisterForm
from forms.login_form import LoginForm
from forms.new_position_form import PositionForm
from forms.order_form import OrderForm

from data.config import *

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(404)
def not_found(error):
    return render_template('static_templates/error_not_found.html')


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def main():
    db_session.global_init("db/database.db")
    api.add_resource(dishes_resources.DishResource, '/api/v1/dishes/<int:dish_id>')
    api.add_resource(dishes_resources.DishesListResource, '/api/v1/dishes')
    app.run(debug=True, port=4050)


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
                        filename = str(datetime.datetime.now().date()) + '_' + str(
                            datetime.datetime.now().time()).replace(':', '').replace('.', '') + '.' + \
                                   file.filename.split('.')[1]
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        file.save('static/' + file_path)

                        db_sess = db_session.create_session()
                        dish = Dish()
                        dish.title = form.title.data
                        dish.description = form.description.data
                        dish.weight = form.weight.data
                        dish.price = form.price.data
                        dish.structure = form.structure.data
                        dish.type = db_sess.query(Type).filter(Type.id == int(form.type.data)).first()
                        dish.image = Image(path=file_path)

                        db_sess.add(dish)
                        db_sess.commit()
                except RequestEntityTooLarge:
                    flash('Загружаемый файл слишком большой.')
            return render_template('static_templates/item_added.html')
        return render_template('new_position.html', form=form)
    else:
        return redirect('/')


@app.route('/items/<string:type>')
def items_list(type):
    db_sess = db_session.create_session()

    types = {
        'rolls': 'Роллы',
        'pizza': 'Пицца',
        'sets': 'Наборы',
        'snacks': 'Салаты и закуски'
    }
    data = db_sess.query(Dish).join(Image, Image.id == Dish.image_id) \
        .join(Type, Type.id == Dish.type_id) \
        .filter(Type.title == types[type]) \
        .options(joinedload(Dish.image)) \
        .all()
    # print(data)
    if not data:
        return render_template('static_templates/error_not_found.html')
    return render_template('items_list.html', type=type, data=data)


def get_item_from_cookies():
    data = []
    total_price = 0
    if 'basket' in session:
        basket_items = set(session['basket'])
        for item in basket_items:
            data.append({
                'id': item,
                'qnt': session['basket'].count(item)
            })

        db_sess = db_session.create_session()
        get_position = db_sess.query(Dish).filter(Dish.id.in_(basket_items))

        # я не смогла придумать как передавать позиции в меню вместе с количеством на фронтенд, поэтому будем вот так грустно делать
        for i in range(len(data)):
            for dish in get_position:
                if data[i]['id'] == dish.id:
                    data[i]['item'] = dish
                    total_price += (data[i]['qnt'] * dish.price)
                    break
        session['total_price'] = total_price
    return data, total_price


@app.route('/basket')
def basket():
    data, total_price = get_item_from_cookies()
    return render_template('basket.html', data=data, total_price=total_price)


@app.route('/clear-basket')
def clear_basket():
    session['basket'] = []
    session.modified = True
    return redirect(request.referrer or url_for('index'))


@app.route('/add-to-basket/<int:product_id>')
def add_to_basket(product_id):
    if 'basket' not in session:
        session['basket'] = []

    session['basket'].append(product_id)
    session.modified = True
    # print('OK')
    return redirect(request.referrer or url_for('index'))


@app.route('/delete-from-basket/<int:product_id>')
def delete_from_basket(product_id):
    for id in session['basket']:
        if id == product_id:
            session['basket'].remove(product_id)
            break
    session.modified = True
    return redirect('/basket')


@app.route('/registrate_order', methods=['GET', 'POST'])
def registrate_order():
    '''Create order and its details to the database'''
    form = OrderForm()
    data, total_price = get_item_from_cookies()
    if form.validate_on_submit():

        # check is correct address or not
        try:
            address = search_object(form.address.data)
        except AddressError:
            return render_template('order_registration.html', error='Некорректный адрес')

        # Create new order, then get its id and use it to create order details
        db_sess = db_session.create_session()
        order = Order(
            delivery_address=address,
            customer_id=current_user.id if current_user.is_authenticated else -1,
            datetime=datetime.datetime.now(),
            comment=form.type_of_paid.data,
            status=0,
            total_amount=total_price
        )

        db_sess.add(order)
        db_sess.commit()

        id_order = order.id
        db_sess = db_session.create_session()
        for item in data:
            order_detail = Detail(
                order_id=id_order,
                item_id=item['item'].id,
                quantity=item['qnt']
            )
            db_sess.add(order_detail)
            db_sess.commit()
        session.clear()
        return render_template('order_created.html')
    return render_template('order_registration.html', form=form, data=data, total_price=total_price)


@app.route('/active_orders')
@login_required
def active_orders():  # TODO: Сделать форму
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
