# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt

import pytest
from {{cookiecutter.app_name}}.apps.models import Role, User

from .factories import UserFactory


@pytest.mark.usefixtures("db")
class TestUser:
    """User tests."""

    def test_get_by_id(self):
        """Get user by ID."""
        user = User(username="foo", email="foo@bar.com")
        user.save()

        retrieved = User.get_by_id(user.id)
        assert retrieved == user

    def test_created_at_defaults_to_datetime(self):
        """Test creation date."""
        user = User(username="foo", email="foo@bar.com")
        user.save()
        assert bool(user.created_at)
        assert isinstance(user.created_at, dt.datetime)

    def test_password_is_nullable(self):
        """Test null password."""
        user = User(username="foo", email="foo@bar.com")
        user.save()
        assert user.password is None

    def test_factory(self, db):
        """Test user factory."""
        user = UserFactory(password="myprecious")
        db.session.commit()
        assert bool(user.username)
        assert bool(user.email)
        assert bool(user.created_at)
        assert user.active is True
        assert user.check_password("myprecious")

    def test_check_password(self):
        """Check password."""
        user = User.create(username="foo", email="foo@bar.com", password="foobarbaz123")
        assert user.check_password("foobarbaz123") is True
        assert user.check_password("barfoobaz") is False

    def test_full_name(self):
        """User full name."""
        user = UserFactory(first_name="Foo", last_name="Bar")
        assert user.full_name == "Foo Bar"

    def test_roles(self):
        """Add a role to a user."""
        role = Role(name="admin")
        role.save()
        user = UserFactory()
        user.roles.append(role)
        user.save()
        assert role in user.roles

    def test_roles_repr(self):
        """Check __repr__ output for Role."""
        role = Role(name="user")
        assert role.__repr__() == "<Role(user)>"

    def test_user_repr(self):
        """Check __repr__ output for User."""
        user = User(username="foo", email="foo@bar.com")
        assert user.__repr__() == "<User('foo')>"

    def test_get_or_create(self):
        user, is_created = User.get_or_create(username="foo-1", email="foo-1@bar.com")

        assert is_created is True

        new_user, is_created = User.get_or_create(
            username="foo-1", email="foo-1@bar.com"
        )
        assert new_user == user
        assert is_created is False

    def test_create_or_update(self):
        user, is_created = User.update_or_create(
            username="foo-1", email="foo-1@bar.com", defaults={"first_name": "F"}
        )
        assert user.username == "foo-1"
        assert is_created is True
        assert user.first_name == "F"

        new_user, is_created = User.update_or_create(
            username="foo-1", email="foo-1@bar.com", defaults={"first_name": "L"}
        )
        assert user.username == "foo-1"
        assert is_created is False
        assert user.first_name == "L"
        assert new_user == user
