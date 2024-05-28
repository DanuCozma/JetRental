from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase

from db import db


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id_user = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(100))
    registration_date = db.Column(db.TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    last_login = db.Column(db.TIMESTAMP)
    is_admin = db.Column(db.Boolean, default=False)

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()


class Jets(Base):
    __tablename__ = "jets"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.Integer)
    color = db.Column(db.String(50))
    engine = db.Column(db.String(50))
    price = db.Column(db.Integer)
    image_url = db.Column(db.String(255))
    state = db.Column(db.Enum('available', 'rented', name='jet_state'), default='available')

    def rent_out(self):
        self.state = 'rented'


class Rentals(Base):
    __tablename__ = 'rentals'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id_user'), nullable=False)
    user_fullname = db.Column(db.String(50), nullable=True)
    jet_id = db.Column(db.Integer, db.ForeignKey('jets.id'), nullable=False)
    jet_model = db.Column(db.String(50), nullable=False)
    jet_name = db.Column(db.String(100), nullable=False)
    decorations = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.TIMESTAMP, nullable=False)
    end_date = db.Column(db.TIMESTAMP, nullable=True)
    price_per_day = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    rental_days = db.Column(db.Integer, nullable=False)
    # Define relationships using string-based references
    jet = db.relationship('Jets', backref=db.backref('rentals', lazy=True))
    user = db.relationship('User', backref=db.backref('rentals', lazy=True))


