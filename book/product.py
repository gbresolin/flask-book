import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    session)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from book.auth import login_required
from book.db import get_db

bp = Blueprint('product', __name__)


@bp.route('/search', methods=['GET', 'POST'])
def search():
    query = "%" + request.args['q'] + "%"

    db = get_db()
    cats = db.execute(
        'SELECT id, name'
        ' FROM category'
        ' ORDER BY name DESC'
    ).fetchall()

    searches = db.execute(
        'SELECT *'
        ' FROM product p JOIN user u ON p.author_id = u.id'
        ' where name like ? OR description like ?', (query, query,)
    ).fetchall()
    if not searches:
        flash('Pas de résultats trouvés pour ' + query.replace("%", ""), 'danger')
    return render_template('product/search.html', searches=searches, query=query.replace("%", ""), cats=cats)


@bp.route('/<int:id>/detail', methods=('GET', 'POST'))
def detail(id):
    db = get_db()

    comments = db.execute(
        'SELECT c.id, comment, username'
        ' FROM comment c JOIN user u ON c.author_id = u.id'
        ' JOIN product p ON c.product_id = ?'
        ' GROUP BY comment',
        (id,)
    ).fetchall()

    cats = db.execute(
        'SELECT id, name'
        ' FROM category'
        ' ORDER BY name DESC'
    ).fetchall()

    details = db.execute(
        'SELECT p.id, name, description, price, state, image, created, author_id, username'
        ' FROM product p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchall()
    return render_template('product/detail.html', details=details, title=id, cats=cats, comments=comments)


@bp.route('/')
def index():
    db = get_db()
    products = db.execute(
        'SELECT p.id, name, description, price, state, image, created, author_id, username'
        ' FROM product p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    db = get_db()
    cats = db.execute(
        'SELECT id, name'
        ' FROM category'
        ' ORDER BY name DESC'
    ).fetchall()

    return render_template('product/home.html', products=products, cats=cats)


@bp.route('/inventory')
@login_required
def inventory():
    user_id = session.get('user_id')
    db = get_db()
    products = db.execute(
        'SELECT p.id, name, description, price, state, image, created, author_id, username'
        ' FROM product p JOIN user u ON p.author_id = u.id'
        ' WHERE author_id = ?'
        ' ORDER BY created DESC'
        , (user_id,)
    ).fetchall()

    if not products:
        flash('Vous n\'avez pas encore de livre en vente.', 'danger')

    return render_template('product/inventory.html', products=products)


def get_product(id, check_author=True):
    product = get_db().execute(
        'SELECT p.id, name, description, price, state, created, author_id, username'
        ' FROM product p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if product is None:
        abort(404, "Le produit id {0} n'existe pas.".format(id))

    if check_author and product['author_id'] != g.user['id']:
        abort(403)

    return product


def get_image(id):
    get_product(id)
    image = get_db().execute(
        'SELECT image'
        ' FROM product'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    return image


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    product = get_product(id)

    state_list = ['Neuf', 'Très bon état', 'Bon état', 'Etat correct', 'Mauvais état']

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        state = request.form['state']
        error = None

        if not name:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE product SET name = ?, description = ?, price = ?, state = ?'
                ' WHERE id = ?',
                (name, description, price, state, id)
            )
            db.commit()
            flash('Modification réussie !', 'success')
            return redirect(url_for('product.inventory'))

    return render_template('product/update.html', product=product, state_list=state_list)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_product(id)
    get_image(id)
    db = get_db()
    file = get_image(id)
    location = "book/static/uploads"
    db.execute('DELETE FROM product WHERE id = ?', (id,))
    for filename in file:
        os.remove(os.path.join(location, filename))
    db.commit()
    flash('Livre supprimé !', 'success')
    return redirect(url_for('product.inventory'))
