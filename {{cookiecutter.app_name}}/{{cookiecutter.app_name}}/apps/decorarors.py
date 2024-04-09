from functools import wraps

from flask_jwt_extended import get_jwt, verify_jwt_in_request
from {{cookiecutter.app_name}}.initialization.exception import CODE
from {{cookiecutter.app_name}}.utils.http import json_response


def auth(roles: list):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if any([True for role in roles if role in claims.keys()]):
                return fn(*args, **kwargs)
            return (
                json_response(
                    data="",
                    code=CODE.PERMISSION_DENIED.code,
                    error=CODE.PERMISSION_DENIED.message,
                ),
                403,
            )

        return decorator

    return wrapper
