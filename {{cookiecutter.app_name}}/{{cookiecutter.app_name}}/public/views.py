# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

from flask.views import MethodView

from {{cookiecutter.app_name}}.apps.models import User
from {{cookiecutter.app_name}}.utils.http import json_response



class IndexView(MethodView):
    def get(self):
        return json_response(data={"hello": "world"})
