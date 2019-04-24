# To Start virtual environment for this project:
# source /Users/jonathanolson/Projects/Environments/nhl_flask/bin/activate

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flaskext.mysql import MySQL
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flasksite.config import Config

# Initialize database for user login
db = SQLAlchemy()

# Initialize database for stats
# mysql = MySQL()

#Initialize our method for encrypting our submitted passwords
bcrypt = Bcrypt()

#Initialize the login manager
login_manager = LoginManager()

#Set login route for the login required
login_manager.login_view = ('users.login') #Pass the function name of the route.
# Same as we do with the url_for function
login_manager.login_message_category = 'info' #Makes the alerts for required
# login a nice blue alert


mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

#    mysql.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    #Import down here to prevent circular imports
    from flasksite.users.routes import users #Here, we are importing the "users" Blueprint variable
    from flasksite.main.routes import main
    from flasksite.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
