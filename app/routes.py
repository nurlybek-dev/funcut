from flask import Blueprint, render_template, redirect, request, jsonify
from app.services import find_url, shorten_url


bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/<short_url>')
def redir(short_url):
    url = find_url(short_url)
    return redirect(url, code=302)


@bp.route('/shorten', methods=['GET', 'POST'])
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
