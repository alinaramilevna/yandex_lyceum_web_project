import sqlalchemy

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Order(SqlAlchemyBase):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    customer_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    delivery_address = sqlalchemy.Column(sqlalchemy.String)
    total_amount = sqlalchemy.Column(sqlalchemy.Float)
    datetime = sqlalchemy.Column(sqlalchemy.DateTime)
    comment = sqlalchemy.Column(sqlalchemy.Integer)  # Тип оплаты, 0 - наличка, 1 - терминал (картой)
    status_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(
        'statuses.id'))  # 1 - Не подтвержден, 2 - подтвержден (в работе), 3 - доставлен
    user = orm.relationship('User')
    status = orm.relationship('Status')

    def __repr__(self):
        return f'<Order> {self.id} {self.delivery_address} {self.datetime}'
