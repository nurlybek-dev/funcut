import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import Redis

from config import Config

db = SQLAlchemy()
redis = Redis()

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    print(app.config['REDIS_URL'])
    redis = Redis.from_url(app.config['REDIS_URL'])

    from app.cli import init_db_command
    app.cli.add_command(init_db_command)

    from app.routes import bp
    app.register_blueprint(bp)

    return app

from app import models