# -*- coding: utf-8 -*-
"""Database module, including the SQLAlchemy database object and DB-related utilities."""
from typing import Optional, Type, TypeVar

import sqlalchemy as sa

from {{cookiecutter.app_name}}.extensions import db

from .compat import basestring

T = TypeVar("T", bound="PkModel")

# Alias common SQLAlchemy names
Column = db.Column
relationship = db.relationship


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        if commit:
            return self.save()
        return self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit: bool = True) -> None:
        """Remove the record from the database."""
        db.session.delete(self)
        if commit:
            return db.session.commit()
        return
    
    def keys(self):
        return [key for key in self.__table__.columns]

    def to_dict(self):
        d = {}
        for c in self.__table__.c:
            d[c.name] = getattr(self, c.name)
        return d


class Model(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True


class PkModel(Model):
    """Base model class that includes CRUD convenience methods, plus adds a 'primary key' column named ``id``."""

    __abstract__ = True
    id = Column(sa.Integer, primary_key=True)
    created_at = Column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        comment="创建时间",
    )
    updated_at = Column(
        sa.DateTime(timezone=True),
        onupdate=sa.func.now(),
        server_default=sa.func.now(),
        comment="创建时间",
    )

    state = Column(sa.Boolean, server_default="1", comment="是否可用, True: 可用; False: 不可用")

    @classmethod
    def get_by_id(cls: Type[T], record_id) -> Optional[T]:
        """Get record by ID."""
        if any(
            (
                isinstance(record_id, basestring) and record_id.isdigit(),
                isinstance(record_id, (int, float)),
            )
        ):
            return db.session.get(cls, record_id)

            # return cls.query.get(int(record_id))
        return None


def reference_col(
    tablename, nullable=False, pk_name="id", foreign_key_kwargs=None, column_kwargs=None
):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    foreign_key_kwargs = foreign_key_kwargs or {}
    column_kwargs = column_kwargs or {}

    return Column(
        db.ForeignKey(f"{tablename}.{pk_name}", **foreign_key_kwargs),
        nullable=nullable,
        **column_kwargs,
    )
