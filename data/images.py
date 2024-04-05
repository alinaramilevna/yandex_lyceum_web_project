import sqlalchemy

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Image(SqlAlchemyBase):
    __tablename__ = 'images'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    path = sqlalchemy.Column(sqlalchemy.String)
