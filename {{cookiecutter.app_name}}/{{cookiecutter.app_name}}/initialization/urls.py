# -*- coding: utf-8 -*-
""" urls """

from flask import Blueprint, Flask
from {{cookiecutter.app_name}}.apps.user import views as user_views
from {{cookiecutter.app_name}}.public import views as public_views


def make_urls(flask_app: Flask):
    def add_url(url:str, view, blue_print:Blueprint):
        blue_print.add_url_rule(url, view_func=view)

    api_blue = Blueprint("api", __name__, url_prefix="/api")
    add_url("/", public_views.IndexView.as_view("index"), blue_print=api_blue)
    add_url("/user/login", user_views.LoginView.as_view("user_login"), blue_print=api_blue)
    add_url("/user/register", user_views.RegisterView.as_view("user_register"), blue_print=api_blue)
    add_url("/user/logout", user_views.LogoutView.as_view("user_logout"), blue_print=api_blue)
    flask_app.register_blueprint(api_blue)
    
