import os
import json

with open("/etc/config.json") as config_file:
    config = json.load(config_file)

class Config():
    #Create a secret key in order to protect the site against arracks and similar
    SECRET_KEY = config.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = config.get("SQLALCHEMY_DATABASE_URI")

    #Setup email system for password resets -- NOT CURRENTLY FUNCTIONAL
    # MAIL_SERVER = 'smtp.googlemail.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = os.environ.get('EMAIL_USER')
    # MAIL_PASSWORD = os.environ.get('EMAIL_PASS')

