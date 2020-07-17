from flask import (
    Blueprint, flash, g, redirect, render_template, url_for,
    session)

from book.auth import login_required
from book.category import all_category
from book.db import get_db

bp = Blueprint('order', __name__)


@bp.route('/order')
def my_command():
    # On récupère l'ID session de l'utilisateur
    user_id = session.get('user_id')

    db = get_db()
    command = db.execute(
        'SELECT c.id, c.created, p.name, p.price, p.image'
        ' FROM command c'
        ' JOIN user u ON c.author_id = u.id'
        ' JOIN product p ON c.product_id = p.id'
        ' WHERE c.author_id = ?'
        ' ORDER BY p.name ASC'
        , (user_id,)
    ).fetchall()

    totalPrice = 0
    for row in command:
        totalPrice += row[3]

    cats = all_category()
    return render_template('order/index.html', command=command, totalPrice=totalPrice, cats=cats)


# Pour créer une commande à partir du panier
@bp.route('/order/create/<int:id>', methods=('GET', 'POST'))
@login_required
def add_order(id):
    user_id = session.get('user_id')

    db = get_db()
    product_cart = db.execute(
        'SELECT c.product_id'
        ' FROM cart c'
        ' JOIN user u ON c.author_id = u.id'
        ' JOIN product p ON c.product_id = p.id'
        ' WHERE c.author_id = ?'
        ' ORDER BY p.name ASC'
        , (user_id,)
    ).fetchone()

    for item in product_cart:
        # flash(item, 'danger')
        # On valide le(s) produit(s) du panier
        db.execute(
            'INSERT INTO command (product_id, author_id)'
            ' VALUES (?, ?)',
            (item, g.user['id'])
        )

    # On vide le panier
    db.execute('DELETE FROM cart WHERE id = ?', (id,))
    db.commit()
    flash('Merci pour votre commande !', 'success')
    return redirect(url_for('order.my_command'))
