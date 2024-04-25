import datetime
import os

from dotenv import load_dotenv

from flask import Flask, render_template, redirect, request, session, flash, current_app, jsonify, make_response, \
    url_for
from sqlalchemy.orm import joinedload
from flask_restful import Api

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.exceptions import RequestEntityTooLarge

from data import db_session
from api import dishes_resources

from data.users import User
from data.tools import check_phone_number, search_object
from data.dishes import Dish
from data.types import Type
from data.images import Image
from data.orders import Order
from data.order_details import Detail
from data.statuses import Status

from forms.register_user import RegisterForm
from forms.login_form import LoginForm
from forms.new_position_form import PositionForm
from forms.order_form import OrderForm

from data.config import *
from data.mail_sender import send_email

app = Flask(__name__)
api = Api(app)
load_dotenv()
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
    if not os.path.exists('db/database.db'):
        db_session.global_init("db/database.db")
        create_base_data_if_not_exist()
    else:
        db_session.global_init("db/database.db")
    api.add_resource(dishes_resources.DishResource, '/api/v1/dishes/<int:dish_id>')
    api.add_resource(dishes_resources.DishesListResource, '/api/v1/dishes')
    app.run(debug=True, port=4050)


def create_base_data_if_not_exist():
    db_sess = db_session.create_session()
    # create 4 types - rolls, pizza, sets, snacks (and salads)
    types = ['rolls', 'pizza', 'sets', 'snacks']
    for type in types:
        t = Type(title=type)
        db_sess.add(t)

    statuses = ['Ожидает подтверждения', 'Готовиться', 'Доставлен']
    for status in statuses:
        s = Status(title=status)
        db_sess.add(s)
    db_sess.commit()


@app.route('/new-position', methods=['GET', 'POST'])
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
                        dish = Dish(
                            title=form.title.data,
                            description=form.description.data,
                            weight=form.weight.data,
                            price=form.price.data,
                            structure=form.structure.data,
                            type=db_sess.query(Type).filter(Type.id == int(form.type.data)).first(),
                            image=Image(path=file_path)
                        )
                        db_sess.add(dish)
                        db_sess.commit()
                    elif not allowed_file(file.filename):
                        flash('Некорректное расширение файла.')
                except RequestEntityTooLarge:
                    flash('Загружаемый файл слишком большой.')
            return render_template('static_templates/item_added.html')
        return render_template('new_position.html', form=form)
    else:
        return redirect('/')


@app.route('/items/<string:type>')
def items_list(type):
    db_sess = db_session.create_session()
    data = db_sess.query(Dish).join(Image, Image.id == Dish.image_id) \
        .join(Type, Type.id == Dish.type_id) \
        .filter(Type.title == type) \
        .options(joinedload(Dish.image)) \
        .all()
    # print(data)
    if not data:
        return render_template('static_templates/error_not_found.html')
    return render_template('items_list.html', type=type, data=data)


def get_item_from_cookies():
    db_sess = db_session.create_session()
    data = []
    total_price = 0
    if 'basket' in session:
        basket_items = set(session['basket'])
        # print(basket_items)
        for item in basket_items:
            data.append({
                'id': item,
                'qnt': session['basket'].count(item),
                'item': db_sess.query(Dish).filter(Dish.id == item).first()
            })

        db_sess = db_session.create_session()
        get_position = db_sess.query(Dish).filter(Dish.id.in_(basket_items))

        # i could not figure out how to transmit position in item list with its quantity to the frontend, so
        # i have to do it so sad
        for i in range(len(data)):
            for dish in get_position:
                if data[i]['id'] == dish.id:
                    data[i]['item'] = dish
                    total_price += (data[i]['qnt'] * dish.price)
                    break
        session['total_price'] = total_price
        # print(total_price)
    # print(data)
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


@app.route('/registrate-order', methods=['GET', 'POST'])
def registrate_order():
    '''Create order and its details to the database'''
    form = OrderForm()
    data, total_price = get_item_from_cookies()
    if form.validate_on_submit():

        # check is correct address or not
        try:
            address = search_object(form.address.data)
        except IndexError:
            return render_template('order_registration.html', error='Некорректный адрес', form=form)

        # Create new order, then get its id and use it to create order details
        db_sess = db_session.create_session()
        order = Order(
            delivery_address=address,
            customer_id=current_user.id if current_user.is_authenticated else -1,
            datetime=datetime.datetime.now(),
            comment=form.type_of_paid.data,
            status_id=1,
            total_amount=total_price
        )

        db_sess.add(order)
        db_sess.commit()

        id_order = order.id
        db_sess = db_session.create_session()
        data_to_send = []
        for item in data:
            order_detail = Detail(
                order_id=id_order,
                item_id=item['item'].id,
                quantity=item['qnt']
            )
            data_to_send.append((item['item'].title, item['qnt']))
            db_sess.add(order_detail)
            db_sess.commit()

        menu_position = []
        for item in data_to_send:
            menu_position.append(' - '.join([str(i) for i in item]))
        text = f"Ваш заказ #{order.id}nАдрес доставки: {address},nВремя заказа: {datetime.datetime.now()},n Позиции меню: {'n'.join(menu_position)}"
        subject = 'Заказ зарегистрирован'
        send_email(form.email.data, subject, text)
        session.clear()

        return render_template('static_templates/order_created.html')
    return render_template('order_registration.html', form=form, data=data, total_price=total_price)


@app.route('/change-order-status', methods=['GET', 'POST'])
@login_required
def change_order_status():
    if current_user.is_authenticated and current_user.status == "super":
        order_id = request.form.get('order_id')
        new_status_id = request.form.get('new_status')
        if order_id and new_status_id:
            db_sess = db_session.create_session()
            order = db_sess.query(Order).get(order_id)
            if order:
                order.status_id = new_status_id
                db_sess.commit()
                flash('Статус заказа успешно обновлен.', 'success')
        return redirect('orders_list.html')

    else:
        return render_template('index.html')


def get_orders(html: str, *args):
    if current_user.is_authenticated and current_user.status == "super":
        db_sess = db_session.create_session()
        if len(args) == 1:
            orders = db_sess.query(Order).filter(Order.status_id == args[0]).all()
        else:
            orders = db_sess.query(Order).filter(Order.status_id.in_(args)).all()
        # BullshitCode ON
        data = []
        # create dictionary with orders and its details
        for order in orders:
            details = db_sess.query(Detail).filter(Detail.order_id == order.id).all()
            data.append({
                'order': order,
                'details': details
            })
        # BullshitCode OFF

        statuses = db_sess.query(Status).all()
        return render_template(html, data=data, statuses=statuses)
    else:
        return redirect('/')


@app.route('/active-orders')
@login_required
def active_orders():
    return get_orders('orders_list.html', 1, 2)


@app.route('/history-orders')
@login_required
def history_orders():
    return get_orders('orders_list.html', 3)


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
            phone_number=check_phone_number(form.phone_number.data),
            status='user'
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
