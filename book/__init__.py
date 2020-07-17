import os

from flask import Flask, flash, render_template, request, g, url_for
from werkzeug.utils import redirect, secure_filename

from book import category
from book.auth import login_required
from book.db import get_db
from datetime import datetime


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'book.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/about')
    def about():
        return render_template('about.html')

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import product
    app.register_blueprint(product.bp)
    app.add_url_rule('/', endpoint='home')

    from . import admin
    app.register_blueprint(admin.bp)
    app.add_url_rule('/', endpoint='home')

    from . import category
    app.register_blueprint(category.bp)
    app.add_url_rule('/', endpoint='home')

    from . import cart
    app.register_blueprint(cart.bp)
    app.add_url_rule('/', endpoint='home')

    app.config["IMAGE_UPLOADS"] = "book/static/uploads"
    app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
    app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

    error = None

    def allowed_image(filename):
        if not "." in filename:
            return False

        ext = filename.rsplit(".", 1)[1]

        if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
            return True
        else:
            error = 'Format non autorisé !'
            flash(error)

    def allowed_image_filesize(filesize):
        if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
            return True
        else:
            return False

    @app.route('/add-book', methods=('GET', 'POST'))
    @login_required
    def add_book():
        state_list = ['Neuf', 'Très bon état', 'Bon état', 'Etat correct', 'Mauvais état']

        db = get_db()
        categories = db.execute(
            'SELECT c.id, name, author_id'
            ' FROM category c JOIN user u ON c.author_id = u.id'
            ' ORDER BY name DESC'
        ).fetchall()

        if request.method == 'POST':

            if request.files:

                if "filesize" in request.cookies:

                    if not allowed_image_filesize(request.cookies["filesize"]):
                        print("Filesize exceeded maximum limit")
                        return redirect(request.url)

                    image = request.files["image"]

                    if image.filename == "":
                        print("No filename")
                        return redirect(request.url)

                    if allowed_image(image.filename):
                        filename = secure_filename(image.filename)
                        ext = filename.rsplit(".", 1)[1]
                        date = datetime.now()
                        date = date.strftime('%d%m%Y%M%S')
                        new_filename = "book_" + date + ".{}".format(ext)

                        image.save(os.path.join(app.config["IMAGE_UPLOADS"], new_filename))

                        print("Image sauvegardée")

            picture = request.files["image"]
            filename = secure_filename(picture.filename)
            ext = filename.rsplit(".", 1)[1]
            date = datetime.now()
            date = date.strftime('%d%m%Y%M%S')
            img = "book_" + date + ".{}".format(ext)

            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            state = request.form['state']
            category = request.form['category']

            error = None

            if not name:
                error = 'Le nom du livre est obligatoire.'

            if error is not None:
                flash(error)
            else:
                db = get_db()
                db.execute(
                    'INSERT INTO product (name, description, category_id, price, state, image, author_id)'
                    ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (name, description, category, price, state, img, g.user['id'])
                )
                db.commit()
                flash('Livre ajouté !', 'success')
                return redirect(url_for('product.index'))

        return render_template('product/create.html', state_list=state_list, categories=categories)

    @app.route("/upload-image", methods=["GET", "POST"])
    def upload_image():

        if request.method == "POST":

            if request.files:

                if "filesize" in request.cookies:

                    if not allowed_image_filesize(request.cookies["filesize"]):
                        print("Filesize exceeded maximum limit")
                        return redirect(request.url)

                    image = request.files["image"]

                    if image.filename == "":
                        print("No filename")
                        return redirect(request.url)

                    if allowed_image(image.filename):
                        filename = secure_filename(image.filename)
                        ext = filename.rsplit(".", 1)[1]
                        date = datetime.now()
                        date = date.strftime('%d%m%Y%M%S')
                        new_filename = "book_" + date + ".{}".format(ext)

                        image.save(os.path.join(app.config["IMAGE_UPLOADS"], new_filename))

                        print("Image sauvegardée")

                        return redirect(request.base_url)

                    else:
                        print("Le type de fichier n'est pas autorisé !")
                        return redirect(request.url)

        return render_template("upload_image.html")

    # Errors
    @app.errorhandler(404)
    def not_found(e):

        return render_template("error/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):

        return render_template("error/403.html"), 403

    return app
