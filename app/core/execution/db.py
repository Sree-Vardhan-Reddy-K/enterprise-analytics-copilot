from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


class DatabaseExecutionError(Exception):
    pass


class Database:
    """
    Read-only database execution layer.
    Assumes DB user has SELECT-only permissions.
    """

    def __init__(self, database_url: str):
        self.engine: Engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )

    def execute(self, sql: str):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(sql))
                return result.fetchall()
        except SQLAlchemyError as e:
            raise DatabaseExecutionError(str(e))
