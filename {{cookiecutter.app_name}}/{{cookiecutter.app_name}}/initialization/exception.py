# -*- coding: utf-8 -*-
""" exception handler."""


class FlaskAppBaseException(Exception):
    def __init__(self, message) -> None:
        self.message = message


class CODE:
    OK = 0

    class OK:
        code = "0"
        message = "ok"

    class PERMISSION_DENIED:
        code = 10003
        message = "PERMISSION_DENIED"

    class INVALID_USERNAME_PASSWORD:
        code = 10001
        message = "INVALID_USERNAME_PASSWORD"

    class REQUEST_INCORRECT_DATA:
        code = 10002
        message = "REQUEST_INCORRECT_DATA"

    class DUPLICATE_USERNAME:
        code = 10003
        message = "DUPLICATE_USERNAME"