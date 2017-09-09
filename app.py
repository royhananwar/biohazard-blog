from flask import Flask, render_template, flash, redirect, url_for, session, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField

from passlib.hash import sha256_crypt
from functools import wraps

from setup import *

app = Flask(__name__)

# Config Mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = user
app.config['MYSQL_PASSWORD'] = password
app.config['MYSQL_DB'] = 'biohazard'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # return data become dictionary

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


# Check if user is login
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Please, Login first!", category="danger")
            return redirect(url_for('login'))

    return wrap


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("You are now logged out", category="success")
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/category')
def category_index():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get data from db
    # Check how many data do you have, and return it become integer
    result = cur.execute("SELECT * FROM category")

    # Make result become tuple/dict
    categories = cur.fetchall()
    cur.close()
    if result > 0:
        return render_template('categories.html', categories=categories)
    else:
        msg = "No Category Found"
        return render_template('categories.html', msg=msg)


@app.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        # Get value from add_category.html
        category_name = request.form['category_name']

        # Create cursor
        cur = mysql.connection.cursor()

        # Insert to DB
        cur.execute('INSERT INTO category(name) VALUES(%s)', (category_name, ))

        # Save to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        return redirect(url_for('category'))

    return render_template('add_category.html')


@app.route('/articles')
def articles_index():

    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM view_articles")
    articles = cur.fetchall()

    if result > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = "No articles found"
        return render_template('articles.html', msg=msg)


@app.route('/article/<int:article_id>')
def article(article_id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM view_articles WHERE article_id=%s", (article_id, ))
    article = cur.fetchone()

    if result > 0:
        cur.close()
        return render_template('article.html', article=article)
    else:
        cur.close()
        msg = "Error 404!"
        return render_template('article.html', msg=msg)

# class ArticleForm(Form):
#     title = StringField('Title', [validators.Length(min=1, max=50)])
#     body = TextAreaField('Content', [validators.Length(min=20)])
#     category = SelectField('Category', choices=[])


@app.route('/add_article', methods=['GET', 'POST'])
@login_required
def add_article():
    cur = mysql.connection.cursor()
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        category_id = request.form['category_id']

        cur.execute("INSERT INTO articles(title, body, category_id, author) VALUES(%s, %s, %s, %s)",
                    (title, body, category_id, session['username']))

        mysql.connection.commit()
        cur.close()
        return redirect(url_for('articles_index'))
    else:
        cur.execute("SELECT * FROM category")
        categories = cur.fetchall()
        cur.close()

        return render_template('add_article.html', categories=categories)


if __name__ == '__main__':
    app.secret_key = '35000$j7SjhWMbv5PF9NaC$7/M069jMb1IGRbVKb3kZ7jCoPGpZpPbnQmhIFhbBn3B'
    app.run(debug=True)
