# -*- coding: utf-8 -*-
"""models."""

from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from {{cookiecutter.app_name}}.database import Column, PkModel, db, relationship
from {{cookiecutter.app_name}}.extensions import bcrypt

third_role_users = db.Table(
    "third_role_users",
    Column("role_id", sa.Integer, sa.ForeignKey("role.id"), primary_key=True),
    Column("user_id", sa.Integer, sa.ForeignKey("user.id"), primary_key=True),
)


class Role(PkModel):
    """A role for a user."""

    __tablename__ = "role"
    name = Column(
        sa.String(
            64,
        ),
        unique=True,
        comment="角色名, admin(普通管理员), superAdmin(超级管理员), develop(开发者平台登陆), staff(公司内部,无开发者平台账号人员登陆)",
        index=True,
    )

    users: Mapped[List["User"]] = relationship(
        back_populates="roles",
        secondary=third_role_users,
        uselist=True
    )  # type: ignore

    def __init__(self, name, **kwargs):
        """Create instance."""
        super().__init__(name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique sa.String."""
        return f"<Role({self.name})>"


class User(PkModel):
    """A user of the app."""

    __tablename__ = "user"
    username: Mapped[str] = mapped_column(sa.String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(sa.String(80), nullable=True)
    # _password = Column("password", db.LargeBinary(128), nullable=True)
    _password: Mapped[str] = mapped_column("password", sa.String(128), nullable=True)
    first_name: Mapped[str] = mapped_column(sa.String(30), nullable=True)
    last_name: Mapped[str] = mapped_column(sa.String(30), nullable=True)
    active: Mapped[bool] = mapped_column(sa.Boolean(), default=False)

    roles: Mapped[List["Role"]] = relationship(
        back_populates="users",
        secondary=third_role_users,
        uselist=True
    )  # type: ignore

    @hybrid_property
    def password(self):
        """Hashed password."""
        return self._password

    @password.setter  # type: ignore
    def password(self, value):
        """Set password."""
        self._password = bcrypt.generate_password_hash(
            value, rounds=len(value)
        ).decode()

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self._password, value)

    @property
    def full_name(self):
        """Full user name."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        """Represent instance as a unique sa.String."""
        return f"<User({self.username!r})>"

