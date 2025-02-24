import inspect
from typing import TYPE_CHECKING

import edgy
from edgy.conf import settings
from edgy.utils.compat import is_class_and_subclass
from pydantic import BaseModel

from edgy_guardian._internal._module_loading import import_string
from edgy_guardian.exceptions import GuardianImproperlyConfigured
from edgy_guardian.utils import get_content_type_model

if TYPE_CHECKING:
    from edgy_guardian.contenttypes.models import ContentType as BaseContentType

ContentType = get_content_type_model()


class AppConfig(BaseModel):
    """
    Configuration class for the application.

    Attributes:
        name (str): The name of the application.
    """

    __app_models__: dict[str, type[edgy.Model]] = {}

    def get_app_label(self) -> str:
        """
        Returns the name of the application.
        """
        return self.name

    def get_verbose_name(self) -> str:
        """
        Returns the verbose name of the application.
        """
        return self.verbose_name

    def get_model(self, name: str) -> type[edgy.Model]:
        """
        Returns the model from the application.
        """
        try:
            return self.__app_models__[name.capitalize()]
        except KeyError:
            raise GuardianImproperlyConfigured(
                f"Model '{name}' is not configured in '{self.get_app_label()}'."
            ) from None

    def get_models(self) -> list[type[edgy.Model]]:
        """
        Returns the models of the application.
        """
        try:
            location = settings.edgy_guardian.models[self.name]
        except KeyError:
            raise GuardianImproperlyConfigured(f"App '{self.name}' is not configured.") from None

        models: dict[str, type[edgy.Model]] = {}
        module = import_string(location)

        members = inspect.getmembers(
            module,
            lambda attr: is_class_and_subclass(attr, edgy.Model)
            and not attr.meta.abstract
            and not is_class_and_subclass(attr, edgy.ReflectModel),
        )
        for name, model in members:
            models[name] = model
        return models


class Apps:
    """
    A registry of all available apps inside the application.

    This is a simple and yet effective object that stores all the apps
    that are available in the the application application. It is used to store
    the configuration of the apps and to provide a way to access the
    configuration of the apps.
    """

    def __init__(self) -> None:
        self.guardian_apps: list[str] = settings.edgy_guardian.apps
        self.all_models: dict[str, type[edgy.Model]] = settings.edgy_guardian.registry.models
        self.app_configs: dict[str, AppConfig] = {}

        self.configure()

    def configure(self) -> None:
        """
        Configures the apps and their configurations.
        """
        for guardian_app in self.guardian_apps:
            app: AppConfig = import_string(guardian_app)()

            if app.name in self.app_configs:
                raise GuardianImproperlyConfigured(
                    f"There is already an app with the name '{app.name}'. Names must be unique."
                )
            self.app_configs[app.get_app_label()] = app
            app.__app_models__ = app.get_models()

    def get_app_configs(self) -> dict[str, AppConfig]:
        """
        Returns the configurations of all the apps.
        """
        return self.app_configs.values()

    def get_app_config(self, app_label: str) -> AppConfig:
        """
        Returns the configuration of the specified app.
        """
        try:
            return self.app_configs[app_label]
        except KeyError:
            raise GuardianImproperlyConfigured(f"App '{app_label}' is not configured.") from None

    def get_models(self) -> list[type[edgy.Model]]:
        """
        Returns all the models from the registry.
        """
        return list(self.all_models.values())

    def get_model(self, app_label: str, model_name: str) -> type[edgy.Model]:
        """
        Returns the model from the registry of the app config.
        """
        app_config: type[AppConfig] = self.app_configs[app_label]
        return app_config.get_model(model_name)


apps = Apps()


async def manage_content_types() -> None:
    """
    Manages the content types of the application.

    This function is used to manage the content types of the application.
    It creates the content types for all the models that are registered
    with the application.

    This function **must be run** before any other operation that
    involves content types or permissions.

    Usually, using a lifespan event is the best way to run this function.
    """
    from edgy_guardian.contenttypes.models import ContentType

    # Gets all the existing content types already in the database
    existing_content_types: list["BaseContentType"] = await ContentType.query.all()

    # Deleted apps
    deleted_apps: dict[str, str] = {}

    # New apps
    new_apps: dict[str, str] = {}

    # Any possible deleted model
    for ctype in existing_content_types:
        if ctype.app_label not in apps.all_models:
            deleted_apps[ctype.app_label] = ctype.model

    # Making sure we get the new models to be added to the content types table
    for name, model_class in apps.all_models.items():
        if name not in deleted_apps:
            new_apps[name] = model_class.meta.tablename

    # Deleting the content types of the deleted apps
    for app_label, model in deleted_apps.items():
        await ContentType.query.filter(app_label=app_label, model=model).delete()

    # Creating the content types of the new apps
    for name, model in new_apps.items():
        await ContentType.query.get_or_create(app_label=name, model=model)
