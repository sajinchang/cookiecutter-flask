#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# 2023-06-23 21:34:28

__author__ = "SamSa"


from celery import shared_task


@shared_task(name="add_together")
def add_together(a: int, b: int) -> int:
    return a + b
