from datetime import datetime
from typing import Any

import edgy
from esmerald.conf import settings


class User(edgy.Model):
    """
    Base model used for a custom user of any application.
    """

    first_name: str = edgy.CharField(max_length=150)
    last_name: str = edgy.CharField(max_length=150)
    username: str = edgy.CharField(max_length=150, unique=True)
    email: str = edgy.EmailField(max_length=120, unique=True)
    last_login: datetime = edgy.DateTimeField(null=True)
    is_active: bool = edgy.BooleanField(default=True)  # type: ignore
    is_staff: bool = edgy.BooleanField(default=False)  # type: ignore
    is_superuser: bool = edgy.BooleanField(default=False)  # type: ignore

    class Meta:
        registry = settings.registry

    @property
    async def is_authenticated(self) -> bool:
        """
        Always return True.
        """
        return True

    @classmethod
    async def _create_user(cls, username: str, email: str, **extra_fields: Any) -> "User":
        """
        Create and save a user with the given username, email.
        """
        if not username:
            raise ValueError("The given username must be set")
        user: User = await cls.query.create(username=username, email=email, **extra_fields)
        return user

    @classmethod
    async def create_user(
        cls,
        username: str,
        email: str,
        **extra_fields: Any,
    ) -> "User":
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return await cls._create_user(username, email, **extra_fields)

    @classmethod
    async def create_superuser(
        cls,
        username: str,
        email: str,
        **extra_fields: Any,
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return await cls._create_user(username, email, **extra_fields)
