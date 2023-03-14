import os

from flask import Flask
from flask import render_template, redirect, url_for, request
from jinja2 import pass_context
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists,create_database
# from jinja2.filters import context
from flask_paginate import Pagination, get_page_args
from flask_table import Table, Col
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import shutil
from flask_caching import Cache

import os
from faker import Faker

SQLALCHEMY_DATABASE_URI='sqlite:///./database.db'

def validate_database():
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    if not database_exists(engine.url): # Checks for the first time  
        create_database(engine.url)     # Create new DB    
        print("New Database Created")   # Verifies if database is there or not.
    else:
        print("Database Already Exists")

def create_app(test_config=None):
    fake = Faker()
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI,
    )

    cache = Cache(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    db = SQLAlchemy(app)

    class Book(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(250))
        description = db.Column(db.String(250))
        file = db.Column(db.String(250))
        preview = db.Column(db.String(250))

        @staticmethod
        def get_all():
            return Book.query.all()

        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'file': self.file,
                'preview': self.preview,
            }
    
    class TableBooks(Table):
        classes = ['table']
        id = Col('Id', show=False)
        name = Col('name')
        description = Col('description')
        file = Col('file')
        preview = Col('preview')

    with app.app_context():
        # validate_database()
        db.create_all()
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    def table_books_data(page=1, per_page=10):
        data = Book.query.all()
        pagination = Pagination(page=page, per_page=per_page, total=len(data), css_framework='bootstrap4')
        return data, pagination
    
    UPLOADS_PATH = "./static/uploads/files"
    UPLOADS_BOOKS_PATH = "./static/uploads/books"
    UPLOADS_PREVIEW_PATH = "./static/uploads/preview"

    @pass_context
    @app.template_filter('active_url_cls')
    def active_url_cls(context, cls, path):
        if request.path.startswith(path):
            return cls
        else:
            return ""
    
    @app.route('/')
    def index():
        return redirect(url_for("books"))

    @app.route('/books_generate')
    def books_generate():
        for i in range(100):
            record = Book(
                preview="",
                name=fake.paragraph(nb_sentences=1),
                description=fake.paragraph(nb_sentences=2),
                file="book2.pdf",
            )
            db.session.add(record)
        db.session.commit()
        return "OK"

    @app.route('/books_clean')
    def books_clean():
        Book.query.delete()
        db.session.commit()
        return "OK"

    @app.route('/api/books')
    def api_books():
        query = Book.query

        # search filter
        search = request.args.get('search')
        if search:
            query = query.filter(db.or_(
                Book.name.like(f'%{search}%'),
                Book.description.like(f'%{search}%')
            ))
        total = query.count()

        # sorting
        sort = request.args.get('sort')
        if sort:
            order = []
            for s in sort.split(','):
                direction = s[0]
                name = s[1:]
                if name not in ['name', 'description', 'file', 'preview']:
                    name = 'name'
                col = getattr(Book, name)
                if direction == '-':
                    col = col.desc()
                order.append(col)
            if order:
                query = query.order_by(*order)

        # pagination
        start = request.args.get('start', type=int, default=-1)
        length = request.args.get('length', type=int, default=-1)
        if start != -1 and length != -1:
            query = query.offset(start).limit(length)

        # response
        return {
            'data': [i.to_dict() for i in query],
            'total': total,
        }

    @app.route("/books", endpoint="books")
    def books():
        context = {}
        return render_template('books_list.html', context=context)

    @app.route("/books/<id>/show", endpoint="books_show")
    def books_show(id):
        context = {
            'book': Book.query.get(id)
        }
        return render_template('books_show.html', context=context)

    class BookForm(FlaskForm):
        name = StringField('Name', validators=[DataRequired()], render_kw={"class": "form-control"})
        description = StringField('Description', validators=[], render_kw={"class": "form-control"})
        file = StringField('File', validators=[], render_kw={"class": "form-control"})
        submit = SubmitField('Сохранить', render_kw={"class": "btn btn-primary"})

    @app.route("/books/<id>/edit", methods=['GET', 'POST'], endpoint="books_edit")
    def books_edit(id):
        book = Book.query.get(id)
        form = BookForm(obj=book)

        context = {
            'book': book,
            'form': form
        }

        if form.validate_on_submit():
            form.populate_obj(book) # update user object with submitted form data
            db.session.commit() # save changes to database
            return redirect(url_for('books'))
        return render_template('books_edit.html', context=context)

    @app.route("/books/<id>/delete", endpoint="books_delete")
    def books_delete(id):
        book = Book.query.get(id)
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for('books'))
    
    @app.route("/books/<id>/preview", endpoint="books_preview")
    def books_preview(id):
        book = Book.query.get(id)
        if not book.preview:
            from preview_generator.manager import PreviewManager

            # os.path.join(os.getcwd(), 
            cache_path = UPLOADS_PREVIEW_PATH+'/'
            pdf_or_odt_to_preview_path = UPLOADS_BOOKS_PATH+'/'+book.file

            manager = PreviewManager(cache_path, create_folder= True)
            path_to_preview_image = manager.get_jpeg_preview(
                pdf_or_odt_to_preview_path, 
                page=1,
                width=512
            )
            book.preview = os.path.basename(path_to_preview_image)
            db.session.commit()
        return redirect("/"+UPLOADS_PREVIEW_PATH+'/'+book.preview)

    @cache.cached(timeout=50, key_prefix='fn_list_files')
    def fn_list_files(search: str="") -> list:
        p = UPLOADS_PATH
        files = [f for f in os.listdir(p) if os.path.isfile(os.path.join(p, f)) and not f.startswith(".")]
        if search:
            files = [f for f in files if search in f]
        files.sort(key=lambda x: os.path.getmtime(os.path.isfile(os.path.join(p, x))))
        files = [{ 'id': i, 'name': f } for i, f in enumerate(files)]
        return files

    @app.route('/api/storage')
    def api_storage():
        search = request.args.get('search', default="")
        files = fn_list_files(search)
        start = request.args.get('start', type=int, default=1)
        length = request.args.get('length', type=int, default=10)
        page_files = files[start:start+length]
        return {
            'data': page_files,
            'total': len(files),
        }

    class StorageForm(FlaskForm):
        name = StringField('Name', validators=[DataRequired()], render_kw={"class": "form-control"})
        submit = SubmitField('Сохранить', render_kw={"class": "btn btn-primary"})

    @app.route('/storage')
    def storage():
        context = {}
        return render_template('storage_list.html', context=context)

    @app.route("/storage/<id>/show", endpoint="storage_show")
    def books_show(id):
        files = fn_list_files()
        files = list(filter(lambda x: str(x['id'])==id, files))
        if (not files[0]): return ""
        file = files[0]

        context = {
            'file': file
        }
        return render_template('storage_show.html', context=context)
    
    @app.route("/storage/<id>/edit", methods=['GET', 'POST'], endpoint="storage_edit")
    def storage_edit(id):
        files = fn_list_files()
        files = list(filter(lambda x: str(x['id'])==id, files))
        if (not files[0]): return ""
        file = files[0]
        form = StorageForm(name=file['name'])

        context = {
            'book': file,
            'form': form
        }

        if form.validate_on_submit():
            from_name=UPLOADS_PATH+"/"+file['name']
            to_name=UPLOADS_PATH+"/"+form.name.data
            os.rename(from_name, to_name)
            return redirect(url_for('storage'))
        return render_template('storage_edit.html', context=context)

    @app.route("/storage/<id>/delete", endpoint="storage_delete")
    def storage_delete(id):
        files = fn_list_files()
        files = list(filter(lambda x: str(x['id'])==id, files))
        file = files[0]
        os.unlink(UPLOADS_PATH+"/"+file['name'])
        return redirect(url_for('storage'))

    @app.route("/storage/<id>/upload", endpoint="storage_upload")
    def storage_upload(id):
        files = fn_list_files()
        files = list(filter(lambda x: str(x['id'])==id, files))
        file = files[0]
        from_file=UPLOADS_PATH+"/"+file['name']
        to_file=UPLOADS_BOOKS_PATH+"/"+file['name']

        shutil.copyfile(from_file, to_file)
        book=Book(
            name=file['name'],
            description="",
            file=file['name'],
            preview=""
        )

        db.session.add(book)
        db.session.commit()
        return redirect(url_for('storage'))

    return app