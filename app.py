import os

from flask import Flask
from flask import render_template, request, flash, redirect, session, url_for
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)

db_path = 'sqlite:///' + os.path.join(app.root_path, 'database.db')

CONFIG_DICT = dict(
    SQLALCHEMY_DATABASE_URI=db_path,
    SECRET_KEY='development secret key',
    WTF_CSRF_SECRET_KEY='a random string',
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


AuthorForm = model_form(Author, base_class=Form, db_session=db.session)
BookForm = model_form(Book, base_class=Form, db_session=db.session)


@app.route('/')
def index():
    authors = Author.query.all()
    books = Book.query.all()

    return render_template('index.html', authors=authors, books=books)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    form = BookForm(request.form)
    if form.validate_on_submit():
        book = Book(name=form.name.data)
        db.session.add(book)
        db.session.commit()
        flash('Book has been added.')
        return redirect(url_for('index'))
    return render_template('add_book.html', form=form)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    form = AuthorForm(request.form)
    if form.validate_on_submit():
        author = Author(fullname=form.fullname.data)
        db.session.add(author)
        db.session.commit()
        flash('Book has been added.')
        return redirect(url_for('index'))
    return render_template('add_author.html', form=form)


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
