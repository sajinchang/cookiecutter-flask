#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# 2023-06-22 22:45:27

__author__ = "SamSa"

import datetime
import decimal
import uuid

from flask import jsonify
from flask.json.provider import DefaultJSONProvider
from sqlalchemy.engine.result import ScalarResult
from {{cookiecutter.app_name}}.database import PkModel
from {{cookiecutter.app_name}}.initialization.exception import CODE


class JsonEncoder(DefaultJSONProvider):
    @classmethod
    def default(cls, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return str(obj)
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, ScalarResult):
            return tuple(obj)
        elif isinstance(obj, PkModel):
            return obj.to_dict()
        elif isinstance(obj, bytes):
            return obj.decode()
        elif hasattr(obj, "tolist"):
            return obj.to_list()
        elif hasattr(obj, "__getitem__"):
            cls = list if isinstance(obj, (list, tuple)) else dict
            return cls(obj)
        elif hasattr(obj, "__iter__"):
            return tuple(item for item in obj)
        else:
            return super().default(obj)


def json_response(data=None, code=CODE.OK.code, error=None):

    return jsonify(locals())