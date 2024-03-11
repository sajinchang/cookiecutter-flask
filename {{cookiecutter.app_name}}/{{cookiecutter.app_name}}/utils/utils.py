#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# 2023-03-18 21:05:27

__author__ = "SamSa"


class AttrDict(dict):
    # 继承自dict，实现可以通过.来操作元素
    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError(item)

    def __delattr__(self, item):
        self.__delitem__(item)
