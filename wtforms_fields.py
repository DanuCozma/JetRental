from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length, ValidationError

from db_models import User


# def invalid_credentials(form, field):
#    username_entered = form.username.data
#    password_entered = field.data
#
#    user_object = User.query.filter_by(username=username_entered).first()
#    if user_object is None or not check_password_hash(user_object.password_hash, password_entered):
#        raise ValidationError('Invalid username or password. Please try again.')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(message='Username is required'),
        Length(min=4, max=25, message='Username must be between 4 and 25 characters')
    ])

    email = StringField('Email', validators=[
        InputRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])

    password = PasswordField('Password', validators=[
        InputRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters')
    ])

    full_name = StringField('Full name', validators=[InputRequired(message='Full name is required')])

    submit = SubmitField('Register')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Username is already taken. Please choose a different one.')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Email address is already registered. Please use a different one.')


class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[
        InputRequired(message='Username or Email is required')
    ])

    password = PasswordField('Password', validators=[
        InputRequired(message='Password is required')
    ])

    submit = SubmitField('Login')
