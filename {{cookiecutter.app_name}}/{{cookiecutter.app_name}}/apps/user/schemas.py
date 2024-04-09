#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# 2023-07-05 21:21:50

__author__ = "SamSa"

from marshmallow.fields import DateTime
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, fields
from {{cookiecutter.app_name}}.apps import models


class RoleSchema(SQLAlchemyAutoSchema):
    created_at = DateTime(format="%Y-%m-%d %H:%M:%S")
    updated_at = DateTime(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = models.Role
        # include_relationships = True
        # load_instance = True
        # include_fk = True
        exclude = ["created_at", "id", "updated_at"]


class UserSchema(SQLAlchemyAutoSchema):
    roles = fields.Nested(RoleSchema, many=True, read_only=True)
    created_at = DateTime(format="%Y-%m-%d %H:%M:%S")
    updated_at = DateTime(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = models.User
        include_relationships = True
        load_instance = True
        include_fk = True
        exclude = ["_password", "created_at", "id", "updated_at"]
