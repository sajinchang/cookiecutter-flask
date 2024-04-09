# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
import json

from {{cookiecutter.app_name}}.apps.models import User
from {{cookiecutter.app_name}}.initialization.exception import CODE

from .factories import UserFactory


class TestLoggingIn:
    """Login."""

    def test_not_log_in_returns_200(self, user, testapp):
        """Login successful."""
        # Goes to homepage
        content_type = "application/json"

        data = {
            "username": "foobar",
            "email": "foo@bar.com",
            "password": "secret",
            "confirm": "secret",
        }
        res = testapp.post(
            "/api/user/register", params=json.dumps(data), content_type=content_type
        )
        res = testapp.post(
            "/api/user/login", params=json.dumps(data), content_type=content_type
        )

        assert res.status_code == 200
        assert res.json.get("code") == CODE.OK.code
        assert res.json.get("error") is None

    # def test_sees_alert_on_log_out(self, user, testapp):
    #     """Show alert on logout."""

    #     res = testapp.post("/api/user/logout")

    #     assert res.status_code == 200
    #     assert res.json.get("code") == 0
    #     assert res.json.get("error") is None

    def test_sees_error_message_if_password_is_incorrect(self, user, testapp):
        """Show error if password is incorrect."""
        # Goes to homepage
        content_type = "application/json"

        data = {
            "username": "foobar",
            "password": "secret1",
        }
        res = testapp.post(
            "/api/user/login", params=json.dumps(data), content_type=content_type
        )

        # assert res.status_code == 200
        assert res.json.get("error") is not None
        assert res.json.get("code") == CODE.INVALID_USERNAME_PASSWORD.code
        assert "username or password invalid" in res.json.get("error")

    def test_sees_error_message_if_username_doesnt_exist(self, user, testapp):
        """Show error if username doesn't exist."""
        # Goes to homepage
        content_type = "application/json"

        data = {
            "username": "foobar111",
            "password": "secret",
        }
        res = testapp.post(
            "/api/user/login", params=json.dumps(data), content_type=content_type
        )

        assert res.json.get("error") is not None
        assert res.json.get("code") == CODE.INVALID_USERNAME_PASSWORD.code
        assert "username or password invalid" in res.json.get("error")


class TestRegistering:
    """Register a user."""

    def test_can_register(self, user, testapp):
        """Register a new user."""
        old_count = len(User.query.all())
        # Goes to homepage
        content_type = "application/json"

        data = {
            "username": "foobar",
            "email": "foo@bar.com",
            "password": "secret",
            "confirm": "secret",
        }
        res = testapp.post(
            "/api/user/register", params=json.dumps(data), content_type=content_type
        )
        assert res.status_code == 200
        assert res.json.get("code") == CODE.OK.code
        # A new user was created
        assert len(User.query.all()) == old_count + 1

    def test_sees_error_message_if_passwords_dont_match(self, user, testapp):
        """Show error if passwords don't match."""
        # Goes to registration page
        content_type = "application/json"

        data = {
            "username": "foobar",
            "email": "foo@bar.com",
            "password": "secret",
            "confirm": "secret1",
        }
        res = testapp.post(
            "/api/user/register", params=json.dumps(data), content_type=content_type
        )
        assert "error" in res.json
        assert res.json.get("code") == CODE.REQUEST_INCORRECT_DATA.code

    def test_sees_error_message_if_user_already_registered(self, user, testapp):
        """Show error if user already registered."""
        user = User.create(username="foobar", email="foo@bar.com")
        user.save()
        # Goes to registration page
        content_type = "application/json"

        data = {
            "username": "foobar",
            "email": "foo@bar.com",
            "password": "secret",
            "confirm": "secret",
        }
        res = testapp.post(
            "/api/user/register", params=json.dumps(data), content_type=content_type
        )
        assert res.status_code == 200
        assert "error" in res.json
        assert res.json.get("code") == CODE.DUPLICATE_USERNAME.code
        error_infos = res.json.get("error")
        assert CODE.DUPLICATE_USERNAME.message in error_infos
