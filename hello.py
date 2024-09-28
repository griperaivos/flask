from flask import Flask, request, render_template
from markupsafe import escape

# Create a Instance of this class. __name__ is a convenient shortcut for this
app = Flask(__name__)

# Route() tell Flask what URL shoud trigger our function
@app.route("/")
def hello():
    return "Hello Worldu!"

@app.route('/user/<username>')
def show_user_profile(username):
    return f'User {escape(username)}'

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        return do_the_login()
    else:
        return show_the_login_form()