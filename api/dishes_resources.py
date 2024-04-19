from flask import jsonify
from flask_restful import abort
from flask_restful import Resource
from api.dish_parser import parser
from data import db_session
from data.dishes import Dish


def abort_if_dish_not_found(dish_id):
    session = db_session.create_session()
    dish = session.query(Dish).get(dish_id)
    if not dish:
        abort(404, message=f"Item {dish_id} not found")
    return dish


class DishResource(Resource):
    def get(self, dish_id):
        dish = abort_if_dish_not_found(dish_id)
        if dish:
            return jsonify({'dish': dish.to_dict(only=('title', 'description', 'price', 'weight', 'structure'))})

    def delete(self, dish_id):
        abort_if_dish_not_found(dish_id)
        session = db_session.create_session()
        dish = session.query(Dish).get(dish_id)
        session.delete(dish)
        session.commit()
        return jsonify({'success': 'OK'})


class DishesListResource(Resource):
    def get(self):
        session = db_session.create_session()
        dishes = session.query(Dish).all()
        return jsonify({'dishes': [item.to_dict(
            only=('title', 'description', 'price', 'weight', 'structure')) for item in dishes]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        dish = Dish(
            title=args['title'],
            weight=args['weight'],
            description=args['description'],
            structure=args['structure'],
            price=args['price'],
            image_id=args['image_id'],
            type_id=args['type_id']
        )
        session.add(dish)
        session.commit()
        return jsonify({'id': dish.id})
