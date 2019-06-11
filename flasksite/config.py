import os
import json

with open("/etc/mySecrets/myConfig.json") as config_file:
    config = json.load(config_file)

class Config():
    #Create a secret key in order to protect the site against attacks and similar
    SECRET_KEY = config.get("SECRET_KEY")
    # SQLALCHEMY_DATABASE_URI = config.get("SQLALCHEMY_DATABASE_URI") TODO - remove this line

    MYSQL_DATABASE_DB = config.get("MYSQL_DATABASE")
    MYSQL_DATABASE_PASSWORD = config.get("MYSQL_PASSWORD")
    MYSQL_DATABASE_PORT = config.get("MYSQL_PORT")
    MYSQL_DATABASE_HOST = config.get("MYSQL_HOST")
    MYSQL_DATABASE_USER = config.get("MYSQL_USER")

    SQLALCHEMY_DATABASE_URI = (f'mysql+pymysql://{MYSQL_DATABASE_USER}:{MYSQL_DATABASE_PASSWORD}@{MYSQL_DATABASE_HOST}:{MYSQL_DATABASE_PORT}/{MYSQL_DATABASE_DB}')

    # For Tweepy
    my_consumer_key = config.get("my_consumer_key")
    my_consumer_secret = config.get("my_consumer_secret")
    my_access_token = config.get("my_access_token")
    my_access_token_secret = config.get("my_access_token_secret")

    # For recurly
    RECURLY_API_KEY = config.get("recurly_API_KEY")
    RECURLY_SUBDOMAIN = config.get("recurly_SUBDOMAIN")
    RECURLY_DEFAULT_CURRENCY = config.get("recurly_DEFAULT_CURRENCY")

    # For monitoring website
    DEV_EMAIL_ADDRESS = config.get("DEV_EMAIL_ADDRESS")
    DEV_EMAIL_PASSWORD = config.get("DEV_EMAIL_PASSWORD")
    LINODE_TOKEN = config.get("LINODE_TOKEN")
    NHL_LINODE_ID = config.get("NHL_LINODE_ID")
