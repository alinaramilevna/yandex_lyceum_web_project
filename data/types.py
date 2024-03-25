import sqlalchemy

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Type(SqlAlchemyBase):
    __tablename__ = 'types'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    dishes = orm.relationship('Dish', back_populates='type')

    def __repr__(self):
        return f'<Dish> {self.id} {self.title}'
