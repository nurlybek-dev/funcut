from app import db

class Urls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_origin = db.Column(db.String(), nullable=False)
    url_hash = db.Column(db.String(), unique=True)
    url_name = db.Column(db.String(), unique=True)
