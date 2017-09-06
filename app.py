from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('base.html')


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


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        return render_template('register.html', form=form)
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
