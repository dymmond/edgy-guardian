from typing import Any, ClassVar, cast

import edgy

from edgy_guardian._internal._models import BaseGuardianModel
from edgy_guardian.content_types.managers import ContentTypeManager


class AbstractContentType(BaseGuardianModel):
    app_label: str = edgy.CharField(max_length=100)
    model: str = edgy.CharField(max_length=100)

    guardian: ClassVar[Any] = ContentTypeManager()  # noqa

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.app_labeled_name

    @property
    def name(self) -> str:
        """
        Returns the name of the model class.
        This method attempts to instantiate the model class associated with the
        current instance. If the model class cannot be instantiated, it returns
        the model attribute. Otherwise, it returns the name of the model class.

        Returns:
            str: The name of the model class or the model attribute if the class
            cannot be instantiated.
        """

        model = self.model_class()
        if not model:
            return self.model
        return str(model.__class__.__name__)

    @property
    def app_labeled_name(self) -> str:
        """
        Returns the app label name for the current instance.
        This method retrieves the app configuration for the given app label
        and returns the app label name.

        Returns:
            str: The app label name.
        """
        from edgy_guardian.apps import get_apps

        app_config = get_apps().get_app_config(self.app_label)
        return app_config.get_app_name()

    def model_class(self) -> type[edgy.Model]:
        """
        Returns the model class associated with the given app label and model name.
        This method attempts to retrieve the model class using the app label and model name
        stored in the instance. If the model cannot be found, it returns None.

        Returns:
            type[edgy.Model] or None: The model class if found, otherwise None.
        Raises:
            LookupError: If the model cannot be found.
        """
        from edgy_guardian.apps import get_apps

        try:
            return get_apps().get_model(self.app_label, self.model)
        except LookupError:
            return None

    async def get_object_for_this_type(self, **kwargs: Any) -> type[edgy.Model]:
        """
        Retrieve an instance of the model class associated with this type using the provided keyword arguments.

        Args:
            **kwargs (Any): Keyword arguments to filter the guardian.
        Returns:
            type[edgy.Model]: An instance of the model class that matches the provided criteria.
        """

        return cast(type[edgy.Model], await self.model_class().guardian.get(**kwargs))

    async def get_all_objects_for_this_type(self, **kwargs: Any) -> Any:
        """
        Retrieve all objects of the specified type based on the provided filter criteria.

        Args:
            **kwargs (Any): Arbitrary keyword arguments representing the filter criteria.
        Returns:
            QuerySet: A QuerySet containing all objects that match the filter criteria.
        """

        return await self.model_class().guardian.filter(**kwargs)

    @classmethod
    async def configure(cls) -> bool:
        """
        Asynchronously configures the content types for all models in all installed apps.
        Iterates through all app configurations and their respective models, creating or updating
        the content type entries in the database.

        Returns:
            bool: Always returns True.
        """
        from edgy_guardian.apps import get_apps

        for app_config in get_apps().app_configs.items():
            for models in app_config.get_models():
                (
                    await cls.guardian.update_or_create(
                        app_label=app_config.get_app_name(),
                        defaults={"model": models.__name__},
                    ),
                )
        return True


class BaseContentType(AbstractContentType):
    class Meta:
        abstract = True
        unique_together = [("app_label", "model")]
