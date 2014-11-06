from flask import Flask
from flask import render_template
from flask import render_template, request, flash, redirect, session, url_for

app = Flask(__name__)

CONFIG_DICT = dict(
    SECRET_KEY='development secret key',
    USERNAME='admin',
    PASSWORD='default'
)

app.config.update(CONFIG_DICT)

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
