#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# 2023-11-03 11:19:59

__author__ = "SamSa"


# 自定义的解析异常
class ParseError(BaseException):
    def __init__(self, message):
        self.message = message


class ValidationError(ParseError):
    """
    Raised when a validator fails to validate its input.
    """

    def __init__(self, message="", *args, **kwargs):
        ParseError.__init__(self, message, *args, **kwargs)


class StopValidation(ParseError):
    """
    Causes the validation chain to stop.

    If StopValidation is raised, no more validators in the validation chain are
    called. If raised with a message, the message will be added to the errors
    list.
    """

    def __init__(self, message="", *args, **kwargs):
        ParseError.__init__(self, message, *args, **kwargs)
