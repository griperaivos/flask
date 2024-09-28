from flask import Flask, abort, make_response, redirect, request, render_template, session, url_for
from markupsafe import escape
from werkzeug.utils import secure_filename

# Create a Instance of this class. __name__ is a convenient shortcut for this
app = Flask(__name__)

# Route() tell Flask what URL shoud trigger our function
@app.route("/")
def index():
    return "Hello Worldu!"

@app.route('/user/<username>')
def show_user_profile(username):
    return f'User {escape(username)}'

"""  
To render a template you can use the render_template() method
Provide the name of the template and the variables you want to pass to the template
Flask will look for templates in the 'templates' folder.
"""
 
@app.route('/hello')
def show_the_login_form():
    
    return render_template('hello.html')
    # return render_template('hello.html', person=name)


# Method attribute to access form data
@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'

    return render_template('login.html', error=error)

# To access parameters submitted in the URL (?key=value) you can use the 'args' attribute
# Recommended to acess URL parameters with 'get'
searchword = request.args.get('key', '')


"""
You can handle uploaded files with flask easily. 
just make sure not to forget to set the 'enctype="multipart/form-data"' attribute on your HTML form,
othervise the browser will not transmit your files at all.

You can access those files by looking at the 'files' attribute on the request object.
Each uploaded file is stored in that dictionary.
'save()' method that allows you to store that file on the filesystem of the server
"""

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['the_file']
        f.save('/var/www/uploads/uploaded_file.txt')
    return 'ata'


"""
If you want to know how the file was named on the client before it was uploaded to your application
you can access the 'filename' attribute. 
Keep in mind that this value can be FORGED so never ever trust that value.
pass it through the 'secure_filename()' function that Werkzeug provides for you
"""

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['the_file']
        file.save(f"/var/www/uploads/{secure_filename(file.filename)}")
    return 'ata'



"""
To set cookies you can use the 'set_cookie' method of responde objects.
The 'cookies' attribute of request objects is a dictionary with all the cookies the client transmits


'Sessions' in Flask that add some security on top of cookies for you
"""

# Reading cookies
@app.route('/')
def index():
    username = request.cookies.get('username')

# Storing cookies
@app.route('/')
def index():
    # Cookies are in response objects, Flask converts strings into responses, but you can use 'make_response()' to modify them.
    resp = make_response(render_template(...))
    resp.set_cookie('username', 'the username')
    return resp


# To redirect a user to another endpoint, use the 'redirect()' function
# to abort a request early with an error code, use the 'abort()' function
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()

# if you want to customize the error page, you can use the 'errorhandler()' decorator
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

"""
In addition to the request object there is also a second object called 'session' 
wich allows you to store information specific to a user from
one request to the next. 
This is implemented on top of cookies for you and signs the cookies
cryptographically.
What this means is that the user could look at the contents of your cookie but not
modify it, unless they know the secret key used for signing.
"""

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def index():
    if 'username' in session:
        return f'Logged in as {session['username']}'
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
                <form method="post">
                    <p><input type=text name=username>
                    <p><input type=submit value=Login>
                </form>
        '''

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

"""
Your operating system has ways to generate pretty random data based
on a cryptographic random generator. Use the following command
to quickly generate a value for Flask.secret_key (or SECRET_KEY)

python -c "import secrets; print(secrets.token_hex())"

"""