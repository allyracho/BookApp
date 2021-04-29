from flask import Flask
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from bookapp.forms import LoginForm, RegistrationForm



app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
mydb = SQLAlchemy(app)
db_name = "BookAppDB"

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from bookapp import routes

def create_database(app):
    if not path.exists('website/' + db_name):
        mydb.create_all(app=app)
        print('Created Database!')