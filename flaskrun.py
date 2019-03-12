from flasksite import create_app
from flask import url_for

app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) # TODO -- Remove host argument
