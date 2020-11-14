from genericpath import exists
import os
import sqlite3
import click
import random
import string
from flask import Flask, request, redirect, render_template, g, current_app, jsonify
from flask.cli import with_appcontext


###
### TODO: Unique names, update styles
###


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            os.path.join(os.path.curdir, 'urls.sqlite'),
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def shorten_url(url):
    db = get_db()

    hashed = db.execute('SELECT * FROM urls WHERE url_origin = ?', (url, )).fetchone()
    if hashed:
        return hashed['url_hash']

    exist = True
    url_hash = ''
    while exist:
        url_hash = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(9))
        exist = db.execute('SELECT id FROM urls WHERE url_hash = ?', (url_hash, )).fetchone() is not None

    print(f"insert {url} : {url_hash}")
    db.execute('INSERT INTO urls (url_origin, url_hash) VALUES (?, ?)', (url, url_hash))
    db.commit()

    return url_hash

def find_url(short_url):
    db = get_db()
    hashed = db.execute('SELECT * FROM urls WHERE url_hash = ?', (short_url, )).fetchone()
    if hashed:
        return hashed['url_origin']
    return '/'

app = Flask(__name__)
app.teardown_appcontext(close_db)
app.cli.add_command(init_db_command)


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
        url = request.json['url']
        if not url:
            return jsonify({'status': 400, 'error': 'Enter url'})
        url_hash = shorten_url(url)
        return jsonify({'status': 200, 'hash': url_hash})

    return redirect('/')
