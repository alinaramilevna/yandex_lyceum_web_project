import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import os

SqlAlchemyBase = orm.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    # я передумала на mysql делать

    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str)  # SQl - лог в консоль echo=True (меня бесило, я отключила)
    __factory = orm.sessionmaker(bind=engine, expire_on_commit=False)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
