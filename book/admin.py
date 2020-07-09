from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from book.auth import login_required
from book.auth import admin_required
from book.db import get_db

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
    return render_template('administration/index.html', users=users)

@bp.route('/user/<int:id>/delete', methods=('POST',))
@login_required
@admin_required
def delete(id):
        db = get_db()
        db.execute('DELETE FROM user WHERE id = ?', (id,))
        db.commit()
        flash('Utilisateur supprimé !', 'success')
        return redirect(url_for('admin.admin'))
