from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

class CustomSQLAlchemy(SQLAlchemy):
    def migrate(self, app, Base):
        # Create engine
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        inspector = inspect(engine)

        # Create all tables
        Base.metadata.create_all(engine)

        # Check if database exists
        if not inspector.has_table('users'):
            Base.metadata.create_all(engine)

        # Check if tables exist
        existing_tables = inspector.get_table_names()
        if 'users' not in existing_tables or 'jets' not in existing_tables or 'rentals' not in existing_tables:
            Base.metadata.create_all(engine)

db = CustomSQLAlchemy()


class DatabaseConnector:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if self._instance:
            raise Exception(
                "DatabaseConnector instance already exists. Use DatabaseConnector.get_instance() to access the instance.")
        self.db = db
