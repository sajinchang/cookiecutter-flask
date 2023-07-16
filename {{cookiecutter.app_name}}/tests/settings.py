"""Settings module for test app."""
import os

ENV = "development"
TESTING = True
SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/dev.db"
SECRET_KEY = "not-so-secret-in-tests"
BCRYPT_LOG_ROUNDS = (
    4  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
)
DEBUG_TB_ENABLED = False
CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = False
WTF_CSRF_ENABLED = False  # Allows form testing
ENABLE_CORS = True
CORS_OPTIONS = dict()

LOG_DIR = os.path.join(os.path.expanduser("~"), "logs", "{{cookiecutter.app_name}}")

os.makedirs(LOG_DIR, exist_ok=True)


class CeleryConfig(object):
    pass


CELERY_CONFIG = CeleryConfig
