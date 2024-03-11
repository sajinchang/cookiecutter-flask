#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# 2023-05-17 11:20:55


from flask_sqlalchemy.pagination import SelectPagination as _SelectPagination
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.orm import Session


class SelectPagination(object):
    def __init__(
        self,
        page: int = 1,
        per_page: int = 100,
        max_per_page: int = 100,
    ) -> None:
        self.page = page
        self.per_page = per_page
        self.max_per_page = max_per_page

    def make_page(self, stmt, session: Session, marsh: SQLAlchemyAutoSchema):
        p = _SelectPagination(
            page=self.page,
            per_page=self.per_page,
            max_per_page=self.max_per_page,
            select=stmt,
            session=session,
        )
        if marsh:
            _m = marsh()  # type: ignore
            d = _m.dump(p.items, many=True)
        else:
            d = p.items
        data = {
            "items": d,
            "has_next": p.has_next,
            "has_prev": p.has_prev,
            "pages": p.pages,
            "total": p.total,
        }

        return data
