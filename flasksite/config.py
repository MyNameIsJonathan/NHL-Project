import os
import json

with open("/etc/config.json") as config_file:
    config = json.load(config_file)

class Config():
    #Create a secret key in order to protect the site against arracks and similar
    SECRET_KEY = config.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = config.get("SQLALCHEMY_DATABASE_URI")

    MYSQL_DATABASE = config.get["MYSQL_DATABASE"]
    MYSQL_PASSWORD = config.get["MYSQL_PASSWORD"]
    MYSQL_PORT = config.get["MYSQL_PORT"]
    MYSQL_HOST = config.get["MYSQL_HOST"]
    MYSQL_USER = config.get["MYSQL_USER"]

