# -*- coding: utf-8 -*-
""" exception handler."""


class FlaskAppBaseException(Exception):
    def __init__(self, message) -> None:
        self.message = message


class CODE:
    OK=0
    INVALID_USERNAME_PASSWORD = 10001

    REQUEST_INCORRECT_DATA = 10002
