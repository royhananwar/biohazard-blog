from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

from setup import *

app = Flask(__name__)

# Config Mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = user
app.config['MYSQL_PASSWORD'] = password
app.config['MYSQL_DB'] = 'biohazard'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' #return data become dictionary

# init MySQL
mysql = MySQL(app)


# Home Page
@app.route('/')
def home():
    return render_template('base.html')


# Make form for registration
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('E-Mail', [validators.Length(min=8, max=32)])
    username = StringField('Username', [validators.Length(min=4, max=32)])
    password = PasswordField('Password', [
        validators.Length(min=6, max=32),
        validators.DataRequired(),
        validators.EqualTo('confirm', message="Password do not match")
    ])
    confirm = PasswordField('Confirm Password')


# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.hash(str(form.password.data))

        # Create cursor DB
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password) "
                    "VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('You are now registered and can login', category='success')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get data from /login if 'POST'
        username = request.form['username']
        password_request = request.form['password']
        # Create cursor db
        cur = mysql.connection.cursor()
        result = cur.execute('SELECT * FROM users WHERE username=%s', (username,))

        if result > 0:
            # Get data from DB
            data = cur.fetchone()
            password = data['password']

            # Check password_request == password from database
            if sha256_crypt.verify(password_request, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash("You are now Logged in!", category="success")

                # close connection
                cur.close()

                return redirect(url_for('dashboard'))

            else:
                # password not same
                error = 'PASSWORD DOES NOT MATCH'
                return render_template('login.html', error=error)

        else:
            error = 'USERNAME NOT FOUND'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You are now logged out", category="success")
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.secret_key = '35000$j7SjhWMbv5PF9NaC$7/M069jMb1IGRbVKb3kZ7jCoPGpZpPbnQmhIFhbBn3B'
    app.run(debug=True)
