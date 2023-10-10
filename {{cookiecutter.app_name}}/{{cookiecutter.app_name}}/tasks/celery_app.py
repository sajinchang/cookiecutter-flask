#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# 2023-06-27 10:10:45

__author__ = "SamSa"


import logging
import os
from typing import Any

from celery.signals import worker_process_init

from {{cookiecutter.app_name}}.app import create_app
from {{cookiecutter.app_name}}.extensions import celery_app, db, set_logger

from . import task

flask_app = create_app()

app = celery_app


@worker_process_init.connect
def reset_db_connection_pool(**kwargs: Any) -> None:
    with flask_app.app_context():
        db.engine.dispose()
        LOG_DIR = flask_app.config["LOG_DIR"]
        set_logger(
            logging.getLogger("celery"),
            os.path.join(LOG_DIR, "celery.log"),
            stream=True,
            formatted=True,
        )
