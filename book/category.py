from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    session)
from werkzeug.exceptions import abort

from book.auth import login_required
from book.db import get_db

bp = Blueprint('category', __name__)


@bp.route('/category/index')
@login_required
def get_cat_user():
    user_id = session.get('user_id')
    db = get_db()
    categories = db.execute(
        'SELECT c.id, name, author_id'
        ' FROM category c JOIN user u ON c.author_id = u.id'
        ' WHERE author_id = ?'
        ' ORDER BY name ASC'
        , (user_id,)
    ).fetchall()

    if not categories:
        flash('Vous n\'avez pas encore ajouté de catégorie.', 'danger')

    return render_template('category/index.html', categories=categories)


@bp.route('/category/<int:id>')
def detail(id):
    db = get_db()
    cats = db.execute(
        'SELECT id, name'
        ' FROM category'
        ' ORDER BY name DESC'
    ).fetchall()

    details = db.execute(
        'SELECT *'
        ' FROM product JOIN category ON product.category_id = category.id'
        ' WHERE category_id = ?',
        (id,)
    ).fetchall()

    if not details:
        flash('Pas de livres trouvés pour cette catégorie.', 'danger')

    return render_template('category/detail.html', details=details, title=id, cats=cats)


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
            flash('Catégorie ajoutée !', 'success')
            return redirect(url_for('category.get_cat_user'))

    return render_template('category/create.html')


@bp.route('/category/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    category = get_cat(id)

    if request.method == 'POST':
        name = request.form['categorie']
        error = None

        if not name:
            error = 'Category is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE category SET name = ?'
                ' WHERE id = ?',
                (name, id)
            )
            db.commit()
            flash('Catégorie modifiée !', 'success')
            return redirect(url_for('category.get_cat_user'))

    return render_template('category/update.html', category=category)


@bp.route('/category/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_cat(id)
    db = get_db()
    db.execute('DELETE FROM category WHERE id = ?', (id,))
    db.commit()
    flash('Catégorie supprimée !', 'success')
    return redirect(url_for('category.get_cat_user'))
