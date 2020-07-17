import os

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from book.auth import login_required
from book.auth import admin_required
from book.category import all_category
from book.db import get_db
from book.product import get_image

bp = Blueprint('admin', __name__)


@bp.route('/admin')
@login_required
@admin_required
def all():
    db = get_db()
    users = db.execute(
        'SELECT *'
        ' FROM user'
        ' ORDER BY id DESC'
    ).fetchall()

    cats = all_category()
    return render_template('administration/index.html', users=users, cats=cats)


@bp.route('/admin/category')
@login_required
@admin_required
def category():
    db = get_db()
    categories = db.execute(
        'SELECT id, name'
        ' FROM category'
        ' ORDER BY id DESC'
    ).fetchall()

    cats = all_category()
    return render_template('administration/category.html', categories=categories, cats=cats)


@bp.route('/admin/product')
@login_required
@admin_required
def product():
    db = get_db()
    products = db.execute(
        'SELECT id, name, description, price, state'
        ' FROM product'
        ' ORDER BY id DESC'
    ).fetchall()

    cats = all_category()
    return render_template('administration/product.html', products=products, cats=cats)


def get_user(id):
    user = get_db().execute(
        'SELECT id, username, isAdmin'
        ' FROM user'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if user is None:
        abort(404, "Le user id {0} n'existe pas.".format(id))
    return user


@bp.route('/user/<int:id>/delete', methods=('POST',))
@login_required
@admin_required
def delete(id):
    db = get_db()
    db.execute('DELETE FROM user WHERE id = ?', (id,))
    db.commit()
    flash('Utilisateur supprimé !', 'success')
    return redirect(url_for('admin.all'))


@bp.route('/admin/category/<int:id>/delete', methods=('POST',))
@login_required
@admin_required
def delete_category(id):
    db = get_db()
    db.execute('DELETE FROM category WHERE id = ?', (id,))
    db.commit()
    flash('Catégorie supprimée !', 'success')
    return redirect(url_for('admin.category'))


@bp.route('/product/<int:id>/delete', methods=('POST',))
@login_required
@admin_required
def delete_product(id):
    get_image(id)
    file = get_image(id)
    location = "book/static/uploads"
    db = get_db()
    db.execute('DELETE FROM product WHERE id = ?', (id,))
    for filename in file:
        os.remove(os.path.join(location, filename))
    db.commit()
    flash('Livre supprimé !', 'success')
    return redirect(url_for('admin.product'))


@bp.route('/user/<int:id>/update', methods=('GET', 'POST'))
@login_required
@admin_required
def update(id):
    user = get_user(id)

    cats = all_category()

    if request.method == 'POST':
        username = request.form['username']
        admin = request.form['admin']
        error = None

        if not username:
            error = 'Login obligatoire.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE user SET username = ?, isAdmin = ?'
                ' WHERE id = ?',
                (username, admin, id)
            )
            db.commit()
            flash('Modification réussie !', 'success')
            return redirect(url_for('admin.all'))

    return render_template('administration/update-user.html', cats=cats, user=user)
