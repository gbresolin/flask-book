import functools
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from book.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = 0
        db = get_db()
        error = None

        if not username:
            error = 'Veuillez renseigner un login.'
        elif not password:
            error = 'Veuillez renseigner un mot de passe.'
        elif len(password) < 6:
            error = 'Mot de passe trop court.'
        elif re.search('[0-9]', password) is None:
            error = 'Make sure your password has a number in it.'
        elif re.search('[A-Z]', password) is None:
            error = 'Make sure your password has a capital letter in it.'
        elif db.execute(
                'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password, isAdmin) VALUES (?, ?, ?)',
                (username, generate_password_hash(password), admin)
            )
            db.commit()
            flash('Compté créé ! Vous pouvez vous connecter.', 'success')
            return redirect(url_for('auth.login'))

        flash(error, 'danger')

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_admin'] = user['isAdmin']
            return redirect(url_for('home'))

        flash(error, 'danger')

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    user_admin = session.get('user_admin')

    if user_admin == 0:
        g.admin = 0
    else:
        g.admin = get_db().execute(
            'SELECT * FROM user WHERE isAdmin = ?', (user_admin,)
        ).fetchone()

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.admin == 0:
            return render_template("error/403.html"), 403

        return view(**kwargs)

    return wrapped_view
