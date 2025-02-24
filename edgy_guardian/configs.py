from typing import Any

import edgy
from pydantic import BaseModel

obj_setattr = object.__setattr__


class EdgyGuardianConfig(BaseModel):
    model_config: dict[str, Any] = {"extra": "allow", "arbitrary_types_allowed": True}

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
    user_model: str
    """
    The user model class. This should be a string that represents the user model class location.
    """
    permission_model: str
    """
    The permission model class. This should be a string that represents the permission model class location.
    """
    group_model: str | None = None
    """
    The group model class. This should be a string that represents the group model class location.
    """
    content_type_model: str
    """
    The content type model class. This should be a string that represents the content type model class location.
    """

    def register(self, registry: edgy.Registry) -> edgy.Registry:
        """
        Registers the application registry object and returns it.

        This is used after to filter and manage Edgy Guardian models.
        """
        setattr(self, "registry", registry)  # noqa
        return self.registry
