import sqlalchemy

from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class Dish(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'dishes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    weight = sqlalchemy.Column(sqlalchemy.Integer)
    description = sqlalchemy.Column(sqlalchemy.String)
    structure = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    type_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('types.id'))
    image_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('images.id'))
    image = orm.relationship('Image')
    type = orm.relationship('Type')

    def __repr__(self):
        return f'<Dish> {self.id} {self.title}'

    def __json__(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'weight': self.weight,
            'description': self.description,
            'structure': self.structure,
            'type_id': self.type_id,
            'image_id': self.image_id
        }
