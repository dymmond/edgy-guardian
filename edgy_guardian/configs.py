from typing import Any, cast

import edgy
from pydantic import BaseModel, field_validator

from edgy_guardian._internal._module_loading import import_string


class EdgyGuardianConfig(BaseModel):
    model_config: dict[str, Any] = {"extra": "allow"}

    models: dict[str, str] = {}
    """
    Used to understand where the models are located in the application.

    A key-pair value split by the name of the app and the relative path to the models.
    """
    apps: list[str] = []
    """
    Used to understand where the apps are located in the application.

    The apps are the edgy guardian AppsConfig classes.
    """
    user_model: str | type[edgy.Model]
    """
    The user model class. This should be a string that represents the user model class location.
    """
    permission_model: str | type[edgy.Model]
    """
    The permission model class. This should be a string that represents the permission model class location.
    """
    group_model: str | type[edgy.Model]
    """
    The group model class. This should be a string that represents the group model class location.
    """
    content_type_model: str | type[edgy.Model]
    """
    The content type model class. This should be a string that represents the content type model class location.
    """

    @field_validator("user_model")
    @classmethod
    def validate_user_model(cls, value: str) -> edgy.Model:
        if isinstance(value, edgy.Model):
            return value
        return cast(type[edgy.Model], import_string(value))

    @field_validator("permission_model")
    @classmethod
    def validate_permission_model(cls, value: str) -> edgy.Model:
        if isinstance(value, edgy.Model):
            return value
        return cast(type[edgy.Model], import_string(value))

    @field_validator("group_model")
    @classmethod
    def validate_group_model(cls, value: str) -> edgy.Model:
        if isinstance(value, edgy.Model):
            return value
        return cast(type[edgy.Model], import_string(value))

    @field_validator("content_type_model")
    @classmethod
    def validate_content_type_model(cls, value: str) -> edgy.Model:
        if isinstance(value, edgy.Model):
            return value
        return cast(type[edgy.Model], import_string(value))
