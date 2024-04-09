# -*- coding: utf-8 -*-
"""Database module, including the SQLAlchemy database object and DB-related utilities."""
from importlib.metadata import version
from typing import Optional, Type, TypeVar, Any

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.orm.properties import MappedColumn
from sqlalchemy.orm.exc import NoResultFound

from {{cookiecutter.app_name}}.extensions import db

from .compat import basestring

T = TypeVar("T", bound="PkModel")
TModel = TypeVar("TModel", bound="Model")

# Alias common SQLAlchemy names
Column = db.Column
relationship = db.relationship


class ExtendMixin(object):
    @staticmethod
    def _extract_model_params(defaults, **kwargs):
        defaults = defaults or {}
        ret = {}
        ret.update(kwargs)
        ret.update(defaults)
        return ret

    @classmethod
    def _create_object_from_params(cls, session, lookup, params, lock=False):
        session = session or db.session
        obj = cls(**params)
        session.add(obj)
        try:
            session.commit()
            session.flush()
        except IntegrityError:
            session.rollback()
            query = session.query(cls).filter_by(**lookup)
            if lock:
                query = query.with_for_update()
            try:
                obj = query.one()
            except NoResultFound:
                raise
            else:
                return obj, False
        else:
            return obj, True

    @classmethod
    def get_or_create(
        cls, session: Session = None, defaults: Optional[dict] = None, **kwargs
    ):
        """
        get_or_create _summary_

        _extended_summary_

        Args:
            defaults: setattr if created. Defaults to None.
            kwargs: select args

        Returns:
            _description_
        """
        session = session or db.session

        try:
            stmt = sa.select(cls).where(
                *[getattr(cls, k) == v for k, v in kwargs.items()]
            )
            obj = session.execute(stmt).scalar_one()
            return obj, False

        except NoResultFound:
            params = cls._extract_model_params(defaults, **kwargs)
            return cls._create_object_from_params(session, kwargs, params)

    @classmethod
    def update_or_create(cls, session:Session=None, defaults=None, **kwargs):
        session = session or db.session
        defaults = defaults or {}
        with session.begin_nested():
            try:
                obj = session.query(cls).with_for_update().filter_by(**kwargs).one()
            except NoResultFound:
                params = cls._extract_model_params(defaults, **kwargs)
                obj, created = cls._create_object_from_params(
                    session, kwargs, params, lock=True
                )
                if created:
                    return obj, created
            for k, v in defaults.items():
                setattr(obj, k, v)
            session.add(obj)
            session.flush()
        return obj, False


class CRUDMixin(ExtendMixin):
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


class Model(CRUDMixin, db.Model):  # type: ignore
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True

    @classmethod
    def get(cls, **kwds) -> TModel | None:
        cond = [getattr(cls, k) == v for k, v in kwds.items()]
        stmt = sa.select(cls).where(*cond)

        return db.session.execute(stmt).scalar_one_or_none()


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
    tablename, nullable=False, pk_name="id", foreign_key_kwargs=None, column_kwargs=None)->MappedColumn[Any]:
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    foreign_key_kwargs = foreign_key_kwargs or {}
    column_kwargs = column_kwargs or {}

    return mapped_column(
        db.ForeignKey(f"{tablename}.{pk_name}", **foreign_key_kwargs),
        nullable=nullable,
        **column_kwargs,
    )
