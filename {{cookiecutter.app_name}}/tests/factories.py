# -*- coding: utf-8 -*-
"""Factories to help in tests."""
from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory
from {{cookiecutter.app_name}}.apps.models import User
from {{cookiecutter.app_name}}.database import db


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
    """User factory."""

    username = Sequence(lambda n: f"user{n}")
    email = Sequence(lambda n: f"user{n}@example.com")
    active = True

    class Meta:
        """Factory configuration."""

        model = User
