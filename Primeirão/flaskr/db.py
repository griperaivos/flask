# Connect to the Database

import sqlite3

import click
from flask import current_app, g


"""
g is a special object that is a unique for each request.
It is used to store data that might be accessed by multiple functions during the request.
The connection is stored and reused instead of creating a new connection if get_db is called a second time in the same request.

current_app is another special object that points to the Flask application handling the request.
Since you used an application factory, there is no application object when writting the rest of your code.
get_db will be called when the application has been created and is handling a request, so current_app can be used
"""
def get_db():
    if 'db' not in g:
        """
        sqlite3.connect() establishes a connection to the file pointed at by the DATABASE configuration key.
        This file doesn't have to exist yet, and won't until you initialize the database later.
        """
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        """
        sqlite3.Row tells the connection to return rows that behave like dicts.
        This allows accessing the columns by name.
        """
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    """
    open_resource() opens a file relative to the flaskr package, 
    which is useful since you won't necessarily know where that location is when deploying the application later
    """
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# click.command() defines a command line command called init-db
@click.command('init-db')
def init_db_command():
    #Clear the existing data and create new tables.
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    # app.teardown_appcontext() tell Flask to call that function when cleaning up after returning the response.
    app.teardown_appcontext(close_db)
    # app.cli.add_command() adds a new command that can be called with the flask command.
    app.cli.add_command(init_db_command)