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
def hello_world():
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

        return render_template('register.html', form=form)

    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
