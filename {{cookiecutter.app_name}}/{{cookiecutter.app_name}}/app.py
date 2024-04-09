# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""

import logging
import os

from flask import Flask
from {{cookiecutter.app_name}}.initialization import FlaskAppInitializer

logger = logging.getLogger(__name__)


def create_app(config_object=None) -> Flask:
    app = FlaskApp(__name__)
    try:
        # Allow user to override our config completely
        if not config_object:

            config_object = os.getenv("FLASK_SETTING", "{{cookiecutter.app_name}}.settings")
        app.config.from_object(config_object)

        app_initializer = app.config.get("APP_INITIALIZER", FlaskAppInitializer)(app)
        app_initializer.init_app()

        return app

    except Exception as ex:
        logger.exception("Failed to create app")
        raise ex


class FlaskApp(Flask):
    from {{cookiecutter.app_name}}.utils.http import JsonEncoder
    json_provider_class = JsonEncoder


# celery  -A alarm.tasks.celery_app:app worker -Ofair -l INFO
# celery  -A alarm.tasks.celery_app:app beat -l INFO --pidfile /tmp/alarm-celery-beat.pid -s /tmp/celery-beat-schedule
# celery  -A alarm.tasks.celery_app:app flower
# gunicorn -w 2 -b 0.0.0.0  "alarm.app:create_app()"
# gunicorn -c alarm/conf/gunicorn.py "alarm.app:create_app()"
if __name__ == "__main__":
    app = create_app()
    app.run(
        debug=True,
    )
