import os

from flask import Flask
from flask import render_template, request, flash, redirect, session, url_for
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)

CONFIG_DICT = dict(
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.root_path, 'database.db'),
    SECRET_KEY='development secret key',
    USERNAME='admin',
    PASSWORD='default'
)

app.config.update(CONFIG_DICT)
db = SQLAlchemy(app)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(120))

    def __init__(self, fullname):
        self.fullname = fullname

    def __repr__(self):
        return '<Author %r>' % self.fullname


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Book %r>' % self.name


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    # raise Exception(app.config)
    if request.method == 'POST':
        if request.form.get('username', None) != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form.get('password', None) != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['username'] = request.form['username']
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were logged out')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
