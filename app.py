import os
import flask_whooshalchemy
from functools import wraps
from flask import Flask
from flask import render_template, request, flash, redirect, session, url_for
from flask.ext.wtf import Form
from flask.ext.sqlalchemy import SQLAlchemy
from wtforms import StringField, SelectField
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.validators import DataRequired


app = Flask(__name__)

db_path = 'sqlite:///' + os.path.join(app.root_path, 'database.db')

CONFIG_DICT = dict(
    SQLALCHEMY_DATABASE_URI=db_path,
    WHOOSH_BASE=db_path,
    MAX_SEARCH_RESULTS=10,
    SECRET_KEY='development secret key',
    WTF_CSRF_SECRET_KEY='a random string',
    USERNAME='admin',
    PASSWORD='default'
)

app.config.update(CONFIG_DICT)
db = SQLAlchemy(app)

association_table = db.Table(
    'authors_books',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'))
)


class Author(db.Model):
    __tablename__ = 'author'
    __searchable__ = ['fullname']

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(120))
    books = db.relationship('Book', secondary=association_table, backref=db.backref('authors', lazy='dynamic'))

    def __init__(self, fullname):
        self.fullname = fullname

    def get_name(self):
        return self.fullname

    def __repr__(self):
        return '<Author %r>' % self.fullname


class Book(db.Model):
    __tablename__ = 'book'
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def __repr__(self):
        return '<Book %r>' % self.name


flask_whooshalchemy.whoosh_index(app, Author)
flask_whooshalchemy.whoosh_index(app, Book)

AuthorForm = model_form(Author, base_class=Form, db_session=db.session)
BookForm = model_form(Book, base_class=Form, db_session=db.session)


class SearchForm(Form):
    query = StringField('query', validators=[DataRequired()])
    type = SelectField('type', default="book", choices=[('book', 'Books'), ('author', 'Authors')])


# Initial data for application
def init_db():
    authors = ['Mark Lutz', 'Mark Pilgrim', 'Richard L. Halterman', 'Al Sweigart', 'Rafe Kettler', 'Robert Picard',
               'Miguel Grinberg']
    books = ['Learning Python', 'Dive into Python 2', 'Dive into Python 3', 'Learning to Program with Python',
             'Hacking Secret Cyphers with Python', 'Invent Your Own Computer Games With Python',
             'A Guide to Python\'s Magic Methods']
    for author_name in authors:
        author = Author(author_name)
        db.session.add(author)
    for book_name in books:
        book = Book(book_name)
        db.session.add(book)
    db.session.commit()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if session['logged_in']:
                return f(*args, **kwargs)
        except KeyError:
            return redirect(url_for('login'))

    return decorated_function


@app.route('/')
def index():
    search_form = SearchForm()
    authors = Author.query.all()
    books = Book.query.all()
    return render_template('index.html', authors=authors, books=books, search_form=search_form)


@app.route('/books/new', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm(request.form)
    if form.validate_on_submit():
        book = Book(form.name.data)
        db.session.add(book)
        db.session.commit()
        flash('Book has been added.')
        return redirect(url_for('index'))
    return render_template('add_book.html', form=form)


@app.route("/books/<int:book_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.get(book_id)
    form = BookForm(request.form, obj=book)
    if form.validate_on_submit():
        form.populate_obj(book)
        db.session.commit()
        flash('Book has been updated.')
        return redirect(url_for('index'))
    return render_template("edit_book.html", book=book, form=form)


@app.route("/books/<int:book_id>/remove", methods=['POST'])
@login_required
def remove_book(book_id):
    book = Book.query.get(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book has been deleted.')
    return redirect(url_for('index'))


@app.route('/authors/new', methods=['GET', 'POST'])
@login_required
def add_author():
    form = AuthorForm(request.form)
    if form.validate_on_submit():
        author = Author(fullname=form.fullname.data)
        db.session.add(author)
        db.session.commit()
        flash('Book has been added.')
        return redirect(url_for('index'))
    return render_template('add_author.html', form=form)


@app.route("/author/<int:author_id>/edit")
@login_required
def edit_author(author_id):
    author = Author.query.get(author_id)
    form = AuthorForm(obj=author)
    if form.validate_on_submit():
        db.session.add(author)
        db.session.commit()
        flash('Author has been updated.')
        return redirect(url_for('index'))
    return render_template("edit_author.html", form=form, author=author)


@app.route("/authors/<int:author_id>/remove", methods=['POST'])
@login_required
def remove_author(author_id):
    author = Author.query.get(author_id)
    db.session.delete(author)
    db.session.commit()
    flash('Author has been deleted.')
    return redirect(url_for('index'))


@app.route('/search_results/')
def search_results():
    query = request.args.get('query')
    category = request.args.get('type')
    if category == 'book':
        results = Book.query.whoosh_search(query, app.config['MAX_SEARCH_RESULTS']).all()
    elif category == 'author':
        results = Author.query.whoosh_search(query, app.config['MAX_SEARCH_RESULTS']).all()
    else:
        raise Exception('Error category')

    return render_template('search_results.html', query=query, category=category,
                           results=results)


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
    app.run(debug=True)
