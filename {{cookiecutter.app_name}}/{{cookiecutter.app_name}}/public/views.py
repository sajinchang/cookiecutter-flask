# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

from flask.views import MethodView

from {{cookiecutter.app_name}}.apps.user.models import User
from {{cookiecutter.app_name}}.extensions import login_manager
from {{cookiecutter.app_name}}.utils.http import json_response


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


class IndexView(MethodView):
    def get(self):
        return json_response(data={"hello": "world"})
