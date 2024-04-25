import sqlalchemy

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Detail(SqlAlchemyBase):
    __tablename__ = 'order_details'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('orders.id'))
    item_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('dishes.id'))
    quantity = sqlalchemy.Column(sqlalchemy.Integer)
    item = orm.relationship('Dish')
    order = orm.relationship('Order')
