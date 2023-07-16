# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""
import logging
import os
from logging.handlers import RotatingFileHandler

import celery
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


def set_logger(logger, filename: str, stream: bool, formatted: bool):
    file_handler = RotatingFileHandler(
        filename,
        maxBytes=50 * 1014 * 1014,
        backupCount=10,
    )

    if stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)
    if formatted:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(filename)s:%(funcName)s:[line:%(lineno)d] - %(message)s",
            # datefmt="%Y-%m-%d %H:%M:%S.%f %z",
        )
        file_handler.setFormatter(formatter)
        if stream:
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)


APP_DIR = os.path.join(os.path.dirname(__file__), os.path.pardir)
login_manager = LoginManager()
celery_app = celery.Celery()
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
bcrypt = Bcrypt()
debug_toolbar = DebugToolbarExtension()
