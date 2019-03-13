import os

# TODO -- Use config file or remove this code. Look for best way to pass mysql information
# with open("/etc/config.json") as config_file:
#     config = json.load(config_file)

class Config():
    #Create a secret key in order to protect the site against attacks and similar
    # SECRET_KEY = config.get("SECRET_KEY")
    # SQLALCHEMY_DATABASE_URI = config.get("SQLALCHEMY_DATABASE_URI")

    # MYSQL_DATABASE_DB = config.get("MYSQL_DATABASE")
    # MYSQL_DATABASE_PASSWORD = config.get("MYSQL_PASSWORD")
    # MYSQL_DATABASE_PORT = config.get("MYSQL_PORT")
    # MYSQL_DATABASE_HOST = config.get("MYSQL_HOST")
    # MYSQL_DATABASE_USER = config.get("MYSQL_USER")

    SECRET_KEY = os.environ.get("SECRET_KEY")
    MYSQL_DATABASE_PASSWORD = os.environ.get("MYSQL_PASSWORD")
    # MYSQL_DATABASE_DB = config.get("MYSQL_DATABASE")
    # MYSQL_DATABASE_PORT = config.get("MYSQL_PORT")
    # MYSQL_DATABASE_HOST = config.get("MYSQL_HOST")
    # MYSQL_DATABASE_USER = config.get("MYSQL_USER")
