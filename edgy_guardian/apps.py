import inspect
from functools import lru_cache
from typing import Any, cast

import edgy
from edgy.conf import settings
from edgy.utils.compat import is_class_and_subclass
from pydantic import BaseModel

from edgy_guardian._internal._module_loading import import_module, import_string
from edgy_guardian.exceptions import GuardianImproperlyConfigured


class AppConfig(BaseModel):
    """
    Configuration class for the application.

    Attributes:
        name (str): The name of the application.
    """

    __app_models__: dict[str, type[edgy.Model]] = {}

    def get_app_name(self) -> str:
        """
        Returns the name of the application.
        """
        return cast(str, self.name)

    def get_app_label(self) -> str | None:
        """
        Returns the label of the application.
        """
        return cast(str, getattr(self, "label", None))

    def get_verbose_name(self) -> str:
        """
        Returns the verbose name of the application.
        """
        return cast(str, self.verbose_name)

    def __filter_model(self, condition: Any) -> list[edgy.Model]:
        return [value for key, value in self.__app_models__.items() if condition(key, value)]

    def get_model(self, name: str) -> type[edgy.Model]:
        """
        Returns the model from the application.
        """

        def condition(key: Any, value: Any) -> Any:
            return value.meta.tablename == name

        try:
            return cast(type[edgy.Model], self.__filter_model(condition)[0])
        except (KeyError, IndexError):
            raise GuardianImproperlyConfigured(
                f"Model '{name}' is not configured in '{self.get_app_name()}'."
            ) from None

    def get_models(self) -> dict[str, type[edgy.Model]]:
        """
        Returns the models of the application.
        """
        try:
            location = settings.edgy_guardian.models[self.name.lower()]
        except KeyError:
            raise GuardianImproperlyConfigured(
                f"App '{self.name.lower()}' is not configured."
            ) from None

        models: dict[str, type[edgy.Model]] = {}
        module = import_module(location)

        members = inspect.getmembers(
            module,
            lambda attr: hasattr(attr, "meta")  # type: ignore
            and not attr.meta.abstract
            and attr.meta.registry is not None
            and attr.__name__ in settings.edgy_guardian.registry.models
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

        if self.all_models is None:
            raise GuardianImproperlyConfigured(
                "No models are registered in the registry. Did you run the `edgy_guardian.registry.register(registry)` function?",
            )
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
            self.app_configs[app.get_app_name()] = app
            app.__app_models__ = app.get_models()

    def get_app_configs(self) -> dict[str, AppConfig]:
        """
        Returns the configurations of all the apps.
        """
        return cast(dict[str, AppConfig], self.app_configs.values())

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
        app_config = self.app_configs[app_label]
        return app_config.get_model(model_name)


apps = Apps()


@lru_cache
def get_apps() -> Apps:
    return apps
