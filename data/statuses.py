import sqlalchemy

from .db_session import SqlAlchemyBase


class Status(SqlAlchemyBase):
    __tablename__ = 'statuses'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
