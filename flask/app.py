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
                name=fake.name(),
                description=fake.paragraph(nb_sentences=1),
                file=fake.file_name(extension='pdf'),
                preview=fake.file_name(extension='png'),
            )
            db.session.add(record)
        db.session.commit()
        return "OK"

    @app.route('/books_clean')
    def books_clean():
        Book.query.delete()
        db.session.commit()
        return "OK"

    @app.route("/books", defaults={"page": 1})
    @app.route("/books/<int:page>")
    def books(page):
        context = {}
        context['books'] = []
        # search=False
        page, per_page, offset = get_page_args()

        per_page = 10
        # books = Book.query.all()
        # books = Book.query.paginate(page, 10, True)
        books = Book.query.limit(per_page).offset(offset)
        total = Book.query.count()
        pagination = Pagination(
            page=page, 
            per_page=per_page, 
            total = total,        
            format_total=True,  
            format_number=True,  
            record_name='books',
            # search=search, 
            css_framework='bootstrap4'
        )
        table = TableBooks(books, no_items='')
        context['table']=table
        context['pagination']=pagination
        return render_template('books_list.html', context=context)

    @app.route('/storage')
    def storage():
        context = {}
        context['files'] = []
        return render_template('storage_list.html', context=context)

    return app