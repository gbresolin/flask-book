from flask import (
    Blueprint, flash, g, redirect, render_template, url_for,
    session)

from book.auth import login_required
from book.category import all_category
from book.db import get_db
from book.product import get_product_cart

bp = Blueprint('cart', __name__)


@bp.route('/cart')
def cart():
    user_id = session.get('user_id')
    db = get_db()
    panier = db.execute(
        'SELECT c.id, p.name, p.price, p.image'
        ' FROM cart c'
        ' JOIN user u ON c.author_id = u.id'
        ' JOIN product p ON c.product_id = p.id'
        ' WHERE c.author_id = ?'
        ' ORDER BY p.name ASC'
        , (user_id,)
    ).fetchall()

    totalPrice = 0
    for row in panier:
        totalPrice += row[2]

    cats = all_category()

    return render_template('cart/index.html', panier=panier, totalPrice=totalPrice, cats=cats)


def get_cart(id, check_author=True):
    cart = get_db().execute(
        'SELECT c.id'
        ' FROM cart c JOIN user u ON c.author_id = u.id'
        ' WHERE u.id = ?',
        (id,)
    ).fetchone()

    return cart


@bp.route('/cart/create/<int:id>', methods=('GET', 'POST'))
@login_required
def addCart(id):
    get_product_cart(id)
    user_id = session.get('user_id')
    db = get_db()

    verifexistitem = get_db().execute(
        'SELECT c.product_id'
        ' FROM cart c JOIN user u ON c.author_id = u.id'
        ' WHERE u.id = ?',
        (user_id,)
    ).fetchone()

    if verifexistitem is None:
        db.execute(
            'INSERT INTO cart (product_id, author_id)'
            ' VALUES (?, ?)',
            (id, g.user['id'])
        )
        db.commit()
        flash('Produit ajouté dans votre panier !', 'success')
        return redirect(url_for('cart.cart'))

    else:
        for itemid in verifexistitem:
            if itemid == id:
                flash('Ce produit est déjà dans votre panier.', 'danger')
                return redirect(url_for('cart.cart'))


@bp.route('/cart/delete/<int:id>', methods=('GET', 'POST'))
@login_required
def deleteItem(id):
    get_cart(id)
    db = get_db()
    db.execute('DELETE FROM cart WHERE id = ?', (id,))
    db.commit()
    flash('Article supprimé de votre panier !', 'success')
    return redirect(url_for('cart.cart'))
