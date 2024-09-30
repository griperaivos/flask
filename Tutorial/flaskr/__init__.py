"""
The most straightforward way to create a Flask application is to create a global Flask instance
directly at the top of your code. 
While this is simple and useful in some cases, it can cause some tricky issues as the procjet grows.

Instead of creating a  Flask instance globally, you will create it inside a function.
This function is known as the application factory.
Any configuration, registration, and other setup the application needs will happen inside the function
then the appliication will be returned.
"""


import os

from flask import Flask

def create_app(test_config=None):
    # Create and configure the app

    """
    the app needs to know where it's located to set up some paths
    __name__ is a convenient way to tell it that
    instance_relative_config=True tells the app that configuration files are relative to the instance folder
    The instance folder is located outside the flaskr package and can hold local data that shouldn't be committed
    to version control, such as configuration secrets and the database file.
    """
    app = Flask(__name__, instance_relative_config=True)

    """
    app.config.from_mapping() sets some default configuration that the app will use:
        SECRET_KEY is used by Flask and extensions to keep data safe.
        It's set to 'dev' to provide a convenient value during development,
        but it should be overridden with a random value when deploying.

        DATABASE is the path where the SQLite database file will be saved. 
        It's under app.instance_path, which is the path that Flask has chosen for the instance folder.
        You'll learn more about the database in the nex section.

    """
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        # app.config.from_pyfile() Overrides the default configuration with values taken from the config.py file in the instance folder if it exists.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    # Import and register the blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    return app