from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    login = StringField('Login', validators = [DataRequired(), Length(min = 2, max = 100)])
    password = PasswordField('Password', validators =[DataRequired()])
    confirm_pass = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    name = StringField('Name', validators = [DataRequired()])
    address = StringField('Address', validators = [DataRequired()])
    phone_num = StringField('Phone Number', validators = [DataRequired()])
    birthday = DateTimeField('Birthday', format='%m/%d/%y')
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    login = StringField('Login', validators = [DataRequired()])
    password = PasswordField('Password', validators =[DataRequired()])
    submit = SubmitField('Login')