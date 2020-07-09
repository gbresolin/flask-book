from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    session)
from werkzeug.exceptions import abort

from book.auth import login_required
from book.db import get_db

bp = Blueprint('category', __name__)


@bp.route('/')
def index():
    db = get_db()
    categories = db.execute(
        'SELECT c.id, name, author_id'
        ' FROM category c JOIN user u ON c.author_id = u.id'
        ' ORDER BY name DESC'
    ).fetchall()
    return render_template('product/home.html', categories=categories)


@bp.route('/category/index')
def all():
    user_id = session.get('user_id')
    db = get_db()
    categories = db.execute(
        'SELECT c.id, name, author_id'
        ' FROM category c JOIN user u ON c.author_id = u.id'
        ' WHERE author_id = ?'
        ' ORDER BY name DESC'
        , (user_id,)
    ).fetchall()
    return render_template('category/index.html', categories=categories)


@bp.route('/<int:id>/category', methods=('GET', 'POST'))
def detail(id):
    db = get_db()
    details = db.execute(
        'SELECT *'
        ' FROM product JOIN category ON product.category_id = category.id'
        ' WHERE category_id = ?',
        (id,)
    ).fetchall()
    return render_template('category/detail.html', details=details, title=id)


def get_cat(id, check_author=True):
    product = get_db().execute(
        'SELECT c.id, name, author_id'
        ' FROM category c JOIN user u ON c.author_id = u.id'
        ' WHERE c.id = ?',
        (id,)
    ).fetchone()

    if product is None:
        abort(404, "Product id {0} doesn't exist.".format(id))

    if check_author and product['author_id'] != g.user['id']:
        abort(403)

    return product


@bp.route('/category/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        error = None

        if not name:
            error = 'Le nom de la catégorie est obligatoire.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO category (name, author_id)'
                ' VALUES (?, ?)',
                (name, g.user['id'])
            )
            db.commit()
            return redirect(url_for('category.index'))

    return render_template('category/create.html')


@bp.route('/category/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_cat(id)
    db = get_db()
    db.execute('DELETE FROM category WHERE id = ?', (id,))
    db.commit()
    flash('Catégorie supprimée !', 'success')
    return redirect(url_for('category.index'))
