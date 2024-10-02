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

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        """
        fetchone() returns one row from the query.
        If the query returned no results, it returns None.
        fetchall() will be used, which returns a list of all results
        """
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'

            """
            check_password_hash() hashes the submitted password in the smae way as the stored hash and securely compares them
            If they match, the password is valid
            """
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.' 

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)

    return render_template('auth/login.html')

"""
bp.before_app_request() registers a function that runs before the view function, no matter what URL is requested.
load_logged_in_user checks if a user id is stored in the session and gets that user's data from the database, storing it on g.user, which lasts for the lenght of the request.
If there is no user id, or if the id doesn't exist, g.user will be None
"""
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# checks if the user is logged in
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view