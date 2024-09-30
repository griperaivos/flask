import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

"""
This creates a Blueprint named 'auth'. 
Like the application object, the blueprint needs to know where it's defined
so __name__ is passed as the second argument.
The url_prefix will be prepended to all the URLs associated with the blueprint
"""
bp = Blueprint('auth', __name__, url_prefix='/auth')


"""
@bp.route associates the URL /register with the register view function.
When Flask receives a request to /auth/register, it will call the register view and use the return value as the response
"""
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                """
                db.execute takes a SQL query with ? placeholders for any user input
                and a tuple of values to replace the placeholders with.
                The database library will take care of escaping the values so you are not vulnerable to a SQL injection attack.

                For security, passwords should never be stored in the database directly.
                Instead, generate_password_hash() is used to securely hash the password, and that hash is stored.
                Since this query modifies data, db.commit() needs to be called afterwards to save the changes.
                """
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()

            except db.IntegrityError:
                error = f"User {username} is already registered"
            else:
                return redirect(url_for("auth.login"))
        
        flash(error)
    
    return render_template('auth/register.html')