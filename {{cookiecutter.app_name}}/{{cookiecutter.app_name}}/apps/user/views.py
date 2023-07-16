# -*- coding: utf-8 -*-
"""User views."""

from flask import jsonify
from flask.views import MethodView
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from {{cookiecutter.app_name}}.extensions import db

from . import forms, models, schemas


class RegisterView(MethodView):
    def post(self):
        form = forms.RegisterForm()
        if not form.validate():
            return jsonify(error=form.errors)

        user = models.User.create(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            active=True,
        )
        ma = schemas.UserSchema()
        ma_data = ma.dump(user, many=False)

        return jsonify(data=ma_data)


class LoginView(MethodView):
    @login_required
    def get(self):
        ma = schemas.UserSchema()
        ma_data = ma.dump(current_user, many=False)
        return jsonify(data=ma_data)

    def post(self):
        form = forms.LoginForm()
        if not form.validate():
            return jsonify(error=form.errors)

        stmt = (
            select(models.User)
            .where(models.User.username == form.username.data)
            .options(selectinload(models.User.roles))
        )
        result = db.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return jsonify(error="username or password invalid.")
        elif not user.check_password(form.password.data):
            return jsonify(error="username or password invalid.")

        ma = schemas.UserSchema()
        login_user(user)
        ma_data = ma.dump(user, many=False)

        return jsonify(data=ma_data)


class LogoutView(MethodView):
    def post(self):
        logout_user()

        return jsonify({})
