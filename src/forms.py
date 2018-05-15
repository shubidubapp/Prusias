from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, IntegerField
from wtforms.validators import InputRequired, Email, EqualTo
from wtforms.fields.html5 import EmailField


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired('Please enter your username.')])
    password = PasswordField("Password", validators=[InputRequired('Please enter your password.'),
                                                     EqualTo('re_password', message='Passwords must match')])
    re_password = PasswordField("Password Again", validators=[InputRequired('Please enter your password again.')])
    email = EmailField("Email", validators=[InputRequired('Please enter your email address.'),
                                            Email('This email address does not seem valid.')])


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired('Please enter your username.')])
    password = PasswordField("Password", validators=[InputRequired('Please enter your password.')])


class BuildingForm(FlaskForm):
    id = HiddenField("Id", validators=[InputRequired()])


class SoldierBuildingForm(FlaskForm):
    id = HiddenField("Id")
    count = IntegerField("Count", validators=[InputRequired("You can't produce 0(zero) soldiers!")])


class MatchForm(FlaskForm):
    opponent_id = HiddenField("Id", validators=[InputRequired()])
