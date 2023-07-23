# -*- coding: utf-8 -*-
"""User views."""

from flask.views import MethodView
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from {{cookiecutter.app_name}}.extensions import db
from {{cookiecutter.app_name}}.initialization.exception import CODE
from {{cookiecutter.app_name}}.utils.http import json_response

from . import forms, models, schemas


class RegisterView(MethodView):
    def post(self):
        form = forms.RegisterForm()
        if not form.validate():
            return json_response(error=form.errors, code=CODE.REQUEST_INCORRECT_DATA)

        user = models.User.create(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            active=True,
        )
        ma = schemas.UserSchema()
        ma_data = ma.dump(user, many=False)

        return json_response(data=ma_data)


class LoginView(MethodView):
    @login_required
    def get(self):
        ma = schemas.UserSchema()
        ma_data = ma.dump(current_user, many=False)
        return json_response(data=ma_data)

    def post(self):
        form = forms.LoginForm()
        if not form.validate():
            return json_response(error=form.errors, code=CODE.REQUEST_INCORRECT_DATA)

        stmt = (
            select(models.User)
            .where(models.User.username == form.username.data)
            .options(selectinload(models.User.roles))
        )
        result = db.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return json_response(error="username or password invalid.", code=CODE.INVALID_USERNAME_PASSWORD)
        elif not user.check_password(form.password.data):
            return json_response(error="username or password invalid.", code=CODE.INVALID_USERNAME_PASSWORD)

        ma = schemas.UserSchema()
        login_user(user)
        ma_data = ma.dump(user, many=False)

        return json_response(data=ma_data)


class LogoutView(MethodView):
    def post(self):
        logout_user()

        return json_response({})
