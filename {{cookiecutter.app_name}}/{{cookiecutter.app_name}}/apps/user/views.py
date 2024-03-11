# -*- coding: utf-8 -*-
"""User views."""

from flask import request
from flask.views import MethodView
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from {{cookiecutter.app_name}}.extensions import db
from {{cookiecutter.app_name}}.initialization.exception import CODE
from {{cookiecutter.app_name}}.utils.http import json_response
from {{cookiecutter.app_name}}.utils.wtf import validators
from {{cookiecutter.app_name}}.utils.wtf.parser import Argument, JsonParser

from {{cookiecutter.app_name}}.apps import models
from {{cookiecutter.app_name}}.apps.user import schemas



class RegisterView(MethodView):
    def post(self):
        form, error = JsonParser(
            Argument(
                "username",
                required=True,
                type=str,
                handler=str.strip,
            ),
            Argument(
                "password",
                required=True,
                type=str,
                handler=str.strip,
            ),
            Argument(
                "confirm",
                required=True,
                type=str,
                handler=str.strip,
            ),
            Argument(
                "email",
                required=True,
                type=str,
                handler=str.strip,
            ),
        ).parse(request.json)

        if error:
            return json_response(error=error, code=CODE.REQUEST_INCORRECT_DATA.code)
        if form.confirm != form.password:
            return json_response(
                code=CODE.REQUEST_INCORRECT_DATA.code,
                error="Passwords must match.",
            )
        try:
            user = models.User.create(
                username=form.username,
                email=form.email,
                password=form.password,
                active=True,
            )
        except IntegrityError:
            return json_response(
                code=CODE.DUPLICATE_USERNAME.code,
                error=CODE.DUPLICATE_USERNAME.message,
            )
        ma = schemas.UserSchema()
        ma_data = ma.dump(user, many=False)

        return json_response(data=ma_data)


class LoginView(MethodView):
    # @login_required
    def get(self):
        ma = schemas.UserSchema()
        current_user = get_current_user()
        ma_data = ma.dump(current_user, many=False)
        return json_response(data=ma_data)

    def post(self):
        form, error = JsonParser(
            Argument(
                "username",
                required=True,
                type=str,
                handler=str.strip,
            ),
            Argument(
                "password",
                required=True,
                type=str,
                handler=str.strip,
            ),
        ).parse(request.json)

        if error:
            return json_response(error=error, code=CODE.REQUEST_INCORRECT_DATA.code)

        stmt = (
            select(models.User)
            .where(models.User.username == form.username)
            .options(selectinload(models.User.roles))
        )
        result = db.session.execute(stmt)

        user = result.scalar_one_or_none()

        if not user:
            return json_response(
                error="username or password invalid.",
                code=CODE.INVALID_USERNAME_PASSWORD.code,
            )
        elif not user.check_password(form.password):
            return json_response(
                error="username or password invalid.",
                code=CODE.INVALID_USERNAME_PASSWORD.code,
            )
        role = [i.name for i in user.roles]
        claims = {}
        if "admin" in role:
            claims.setdefault("admin", True)
        elif "develop" in role:
            claims.setdefault("develop", True)

        ma = schemas.UserSchema()
        ma_data = ma.dump(user, many=False)
        access_token = create_access_token(
            identity=form.username, additional_claims=claims
        )
        refresh_token = create_refresh_token(
            identity=form.username, additional_claims=claims
        )
        ma_data.update(access_token=access_token)
        ma_data.update(refresh_token=refresh_token)
        return json_response(data=ma_data)


class LogoutView(MethodView):
    @jwt_required()
    def post(self):
        # 当前令牌登入黑名单
        rds = current_app.redis
        ACCESS_EXPIRES = current_app.config["ACCESS_EXPIRES"]
        jti = get_jwt()["jti"]
        rds.set(jti, "", ex=ACCESS_EXPIRES)
        return json_response({})


class RefreshToken(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        # 获取刷新token
        import jwt

        identity = get_jwt_identity()
        claims = get_jwt()
        access_token = create_access_token(
            identity=identity,
            fresh=False,
            additional_claims={"admin": True}
            if claims.get("admin", False)
            else {"develop": True},
        )
        return json_response(data={"access_token": access_token})