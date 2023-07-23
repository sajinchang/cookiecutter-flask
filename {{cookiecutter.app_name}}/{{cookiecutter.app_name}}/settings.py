# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""
import os
from typing import Dict, Optional
from urllib.parse import quote_plus

from celery.schedules import crontab


def get_env_variable(var_name: str, default: Optional[str] = None) -> str:
    """Get the environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        else:
            error_msg = "The environment variable {} was missing, abort...".format(
                var_name
            )
            raise EnvironmentError(error_msg)


ENV = get_env_variable("FLASK_ENV", default="production")
DEBUG = ENV == "development"
# SQLALCHEMY_DATABASE_URI = env.str("DATABASE_URL")
SECRET_KEY = get_env_variable(
    "SECRET_KEY", default="S8r5V0$kj*`>}%CRx(lNf<e9hMgOQz':/[4UcWG."
)
# SEND_FILE_MAX_AGE_DEFAULT = get_env_variable("SEND_FILE_MAX_AGE_DEFAULT")
BCRYPT_LOG_ROUNDS = get_env_variable("BCRYPT_LOG_ROUNDS", default="13")
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = False
# CACHE_TYPE = "SimpleCache"  # Can be "MemcachedCache", "RedisCache", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = "S8r5V0$kj*`>}%CRx(lNf<e9hMgOQz':/[4UcWG."

DATABASE_DIALECT = get_env_variable("DATABASE_DIALECT", default="mysql+pymysql")
DATABASE_USER = get_env_variable("DATABASE_USER", "root")
DATABASE_PASSWORD = get_env_variable("DATABASE_PASSWORD", "123456")
DATABASE_HOST = get_env_variable("DATABASE_HOST", "localhost")
DATABASE_PORT = get_env_variable("DATABASE_PORT", "3306")
DATABASE_DB = get_env_variable("DATABASE_DB", "alarm")
CELERY_DB = get_env_variable("CELERY_DB", "alarm_celery")

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = "%s://%s:%s@%s:%s/%s" % (
    DATABASE_DIALECT,
    DATABASE_USER,
    quote_plus(DATABASE_PASSWORD),
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_DB,
)

REDIS_HOST = get_env_variable("REDIS_HOST", "localhost")
REDIS_PORT = get_env_variable("REDIS_PORT", "6379")
REDIS_CELERY_DB = get_env_variable("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = get_env_variable("REDIS_RESULTS_DB", "1")

CACHE_TYPE = "redis"
CACHE_DEFAULT_TIMEOUT = 300
CACHE_REDIS_HOST = REDIS_HOST
CACHE_REDIS_PORT = REDIS_PORT
CACHE_REDIS_DB = REDIS_RESULTS_DB


LOG_DIR = get_env_variable(
    "LOG_DIR", os.path.join(os.path.expanduser("~"), "logs", "{{cookiecutter.app_name}}")
)
os.makedirs(LOG_DIR, exist_ok=True)


class CeleryConfig(object):
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    # imports = ("superset.sql_lab",)
    # result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    result_backend = "%s://%s:%s@%s:%s/%s" % (
        "db+mysql+pymysql",
        DATABASE_USER,
        quote_plus(DATABASE_PASSWORD),
        DATABASE_HOST,
        DATABASE_PORT,
        CELERY_DB,
    )
    # result_backend = 'db+mysql://scott:tiger@localhost/foo'
    redis_db = 1
    # result_backend
    worker_redirect_stdouts_level = "info"
    worker_concurrency = 2
    timezone = "Asia/Shanghai"
    task_serializer = "json"
    result_serializer = "json"
    accept_content = ["json"]
    result_expires = 60 * 60
    # worker_prefetch_multiplier = 1
    # task_acks_late = False
    beat_schedule = {
        # "reports.scheduler": {
        #     "task": "reports.scheduler",
        #     "schedule": crontab(minute="*", hour="*"),
        # },
        # "reports.prune_log": {
        #     "task": "reports.prune_log",
        #     "schedule": crontab(minute=10, hour=0),
        # },
        "add": {
            "task": "tasks.task.add_together",
            "schedule": crontab(minute=0, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig


ENABLE_CORS = True
CORS_OPTIONS: Dict = dict()
