# -*- coding: utf-8 -*-
""" urls """

from flask import Flask

from {{cookiecutter.app_name}}.apps.user import views as user_views
from {{cookiecutter.app_name}}.public import views as public_views


def make_urls(flask_app: Flask):
    def add_url(url:str, view):
        flask_app.add_url_rule(url, view_func=view)

    add_url("/", view=public_views.IndexView.as_view("index"))
    add_url("/api/user/login", view=user_views.LoginView.as_view("user_login"))
    add_url("/api/user/register", view=user_views.RegisterView.as_view("user_register"))
    add_url("/api/user/logout", view=user_views.LogoutView.as_view("user_logout"))
    
