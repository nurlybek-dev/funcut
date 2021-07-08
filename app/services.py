import random
import string

from flask import current_app

from app.models import Urls
from app import db, redis

def shorten_url(url, name):
    if name:
        exist = Urls.query.filter_by(url_name=name).first()
        if exist:
            raise ValueError("Custom link already exists")
        db.session.add(Urls(url_origin=url, url_name=name))
        db.session.commit()
        redis.set(name, url, current_app.config['URL_SAFE_TIME'])
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
        redis.set(url_hash, url, current_app.config['URL_SAFE_TIME'])
        return url_hash


def find_url(short_url):
    if redis.exists(short_url):
        return redis.get(short_url)
    hashed = Urls.query.filter((Urls.url_hash == short_url) | (Urls.url_name == short_url)).first()
    if hashed:
        redis.set(short_url, hashed.url_origin, current_app.config['URL_SAFE_TIME'])
        return hashed.url_origin
    return '/'
