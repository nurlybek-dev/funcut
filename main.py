from enum import unique
from genericpath import exists
import os
from os import error
import sqlite3
import click
import random
import string
from flask import Flask, request, redirect, render_template, g, current_app, jsonify
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy


def init_db():
    db.create_all()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def shorten_url(url, name):
    if name:
        exist = Urls.query.filter_by(url_name=name).first()
        if exist:
            raise ValueError("Custom link already exists")
        db.session.add(Urls(url_origin=url, url_name=name))
        db.session.commit()
        return name
    else:
        hashed = Urls.query.filter_by(url_origin=url).filter(Urls.url_hash.isnot(None)).first() 
        if hashed:
            return hashed.url_hash
        exist = True
        url_hash = ''
        while exist:
            url_hash = ''.join(random.choice(
                string.ascii_letters + string.digits) for _ in range(9))
            exist = Urls.query.filter_by(url_hash=url_hash).first() is not None
        db.session.add(Urls(url_origin=url, url_hash=url_hash))
        db.session.commit()

        return url_hash


def find_url(short_url):
    hashed = Urls.query.filter((Urls.url_hash == short_url) | (Urls.url_name == short_url)).first()
    if hashed:
        return hashed.url_origin
    return '/'


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://funcut:funcut@127.0.0.1:5432/funcut'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.cli.add_command(init_db_command)

db = SQLAlchemy(app)


class Urls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_origin = db.Column(db.String(), nullable=False)
    url_hash = db.Column(db.String(), unique=True)
    url_name = db.Column(db.String(), unique=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<short_url>')
def redir(short_url):
    url = find_url(short_url)
    return redirect(url, code=302)


@app.route('/shorten', methods=['GET', 'POST'])
def shorten():
    if request.method == 'POST':
        url = request.json.get('url')
        name = request.json.get('name')
        if not url:
            return jsonify({'status': 400, 'error': 'Enter url'})
        try:
            url_hash = shorten_url(url, name)
        except ValueError as error:
            return jsonify({'status': 400, 'error': str(error)})
        return jsonify({'status': 200, 'hash': url_hash})

    return redirect('/')
