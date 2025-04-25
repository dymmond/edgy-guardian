from typing import Any

import edgy
from pydantic import BaseModel, ConfigDict, model_validator

from edgy_guardian.enums import DefaultEnum

obj_setattr = object.__setattr__


class EdgyGuardianConfig(BaseModel):
    model_config: ConfigDict = {"extra": "allow", "arbitrary_types_allowed": True}

    registry: edgy.Registry | None = None
    """
    The registry that is used to store the models.
    """
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
    user_model: str | None = None
    """
    The user model class. This should be a string that represents the user model class location.
    """
    permission_model: str | None = None
    """
    The permission model class. This should be a string that represents the permission model class location.
    """
    group_model: str | None = None
    """
    The group model class. This should be a string that represents the group model class location.
    """
    content_type_model: str | None = None
    """
    The content type model class. This should be a string that represents the content type model class location.
    """

    @model_validator(mode="after")
    def validate_models(self) -> Any:
        """
        Validates the models and makes sure that they are in the correct format.
        """
        if self.user_model is None:
            self.user_model = DefaultEnum.USER_DEFAULT
        if self.permission_model is None:
            self.permission_model = DefaultEnum.PERMISSION_DEFAULT
        if self.group_model is None:
            self.group_model = DefaultEnum.GROUP_DEFAULT
        if self.content_type_model is None:
            self.content_type_model = DefaultEnum.CONTENT_TYPE_DEFAULT
        return self

    def register(self, registry: edgy.Registry) -> edgy.Registry:
        """
        Registers the application registry object and returns it.

        This is used after to filter and manage Edgy Guardian models.
        """
        setattr(self, "registry", registry)  # noqa
        return self.registry
