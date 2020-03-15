import functools
from flask import Blueprint, request, flash, render_template, url_for, redirect, session, g
from flaskr.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required!'
        elif not password:
            error = 'Password is required!'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username, )
        ).fetchone() is not None:
            error = '{} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) values (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('blog.index'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute(
            'SELECT * FROM user WHERE username == ?', (username,)
        ).fetchone()
        error = None

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapper_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapper_view
