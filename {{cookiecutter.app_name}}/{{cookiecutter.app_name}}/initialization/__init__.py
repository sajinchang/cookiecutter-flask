#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# 2023-06-25 21:07:25

from __future__ import annotations

import logging
import os
import pathlib
from typing import Any

from flask.logging import default_handler

from {{cookiecutter.app_name}} import commands
from {{cookiecutter.app_name}}.extensions import (
    APP_DIR,
    bcrypt,
    cache,
    celery_app,
    db,
    debug_toolbar,
    migrate,
    set_logger,
    jwt_manager
)
from .urls import make_urls

def close_request_session(response):
    # 解决mysql server gone away
    db.session.remove()
    return response
class FlaskAppInitializer(object):  # pylint: disable=too-many-public-methods
    def __init__(self, app) -> None:
        super().__init__()

        self.flask_app = app
        self.config = app.config

    def configure_logging(self):
        logger: logging.Logger = self.flask_app.logger
        logger.removeHandler(default_handler)
        os.makedirs(self.config["LOG_DIR"], exist_ok=True)
        p = pathlib.Path(self.config["LOG_DIR"])
        flask_log = p / "flask.log"
        sa_log = p / "sqlalchemy.log"
        set_logger(logger, flask_log.as_posix(), stream=True, formatted=True)
        set_logger(
            logging.getLogger("sqlalchemy"),
            sa_log.as_posix(),
            stream=False,
            formatted=False,
        )
        # set_logger(logger, "celery", stream=True, formatted=True)

    def pre_init(self) -> None:
        """
        Called before all other init tasks are complete
        """
        self.configure_logging()

    def post_init(self) -> None:
        """
        Called after any other init tasks
        """

    def configure_celery(self) -> None:
        celery_app.config_from_object(self.config["CELERY_CONFIG"])
        celery_app.set_default()
        flask_app = self.flask_app

        # Here, we want to ensure that every call into Celery task has an app context
        # setup properly
        task_base = celery_app.Task

        class AppContextTask(task_base):  # type: ignore
            # pylint: disable=too-few-public-methods
            abstract = True

            # Grab each call into the task and set up an app context
            def __call__(self, *args: Any, **kwargs: Any) -> Any:
                with flask_app.app_context():
                    return task_base.__call__(self, *args, **kwargs)

        celery_app.Task = AppContextTask

    def shell_init(self):
        @self.flask_app.shell_context_processor
        def make_shell_context():
            from {{cookiecutter.app_name}}.apps.user.models import Role, User

            return locals()

    def register_commands(self):
        """Register Click commands."""
        self.flask_app.cli.add_command(commands.test)
        self.flask_app.cli.add_command(commands.lint)

    def register_extensions(self):
        # self.setup_db()
        db.init_app(self.flask_app)
        migrate.init_app(self.flask_app, db=db, directory=APP_DIR + "/migrations")

        cache.init_app(self.flask_app)
        debug_toolbar.init_app(self.flask_app)
        bcrypt.init_app(self.flask_app)
        jwt_manager.init_app(self.flask_app)

    def configure_middleware(self):
        self.flask_app.after_request(close_request_session)
        if self.config["ENABLE_CORS"]:
            from flask_cors import CORS

            CORS(self.flask_app, **self.config["CORS_OPTIONS"])

    def init_urls(self):
        make_urls(self.flask_app)

    def init_app(self):
        self.configure_middleware()
        self.pre_init()
        self.configure_celery()
        self.register_extensions()
        self.init_urls()
        self.shell_init()
        self.post_init()
        self.register_commands()
