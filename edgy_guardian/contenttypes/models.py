from typing import Any, ClassVar

import edgy

from edgy_guardian.apps import apps
from edgy_guardian.contenttypes.managers import ContentTypeManager


class AbstractContentType(edgy.Model):
    app_label: str = edgy.CharField(max_length=100)
    model: str = edgy.CharField(max_length=100)

    query: ClassVar[ContentTypeManager] = ContentTypeManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.app_labeled_name

    @property
    def name(self):
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

        app_config = apps.get_app_config(self.app_label)
        return app_config.get_app_label()

    def model_class(self) -> edgy.Model:
        """
        Returns the model class associated with the given app label and model name.
        This method attempts to retrieve the model class using the app label and model name
        stored in the instance. If the model cannot be found, it returns None.

        Returns:
            type[edgy.Model] or None: The model class if found, otherwise None.
        Raises:
            LookupError: If the model cannot be found.
        """

        try:
            return apps.get_model(self.app_label, self.model)
        except LookupError:
            return None

    async def get_object_for_this_type(self, **kwargs: Any) -> type[edgy.Model]:
        """
        Retrieve an instance of the model class associated with this type using the provided keyword arguments.

        Args:
            **kwargs (Any): Keyword arguments to filter the query.
        Returns:
            type[edgy.Model]: An instance of the model class that matches the provided criteria.
        """

        return await self.model_class().query.get(**kwargs)

    async def get_all_objects_for_this_type(self, **kwargs: Any):
        """
        Retrieve all objects of the specified type based on the provided filter criteria.

        Args:
            **kwargs (Any): Arbitrary keyword arguments representing the filter criteria.
        Returns:
            QuerySet: A QuerySet containing all objects that match the filter criteria.
        """

        return await self.model_class().query.filter(**kwargs)

    def natural_key(self) -> tuple[str, str]:
        """
        Returns a tuple representing the natural key for the content type.
        The natural key is a tuple containing the app label and the model name.

        Returns:
            tuple[str, str]: A tuple containing the app label and the model name.
        """

        return (self.app_label, self.model)

    @classmethod
    async def configure(cls) -> bool:
        """
        Asynchronously configures the content types for all models in all installed apps.
        Iterates through all app configurations and their respective models, creating or updating
        the content type entries in the database.

        Returns:
            bool: Always returns True.
        """

        for app_config in apps.app_configs.items():
            for models in app_config.get_models():
                await cls.query.update_or_create(
                    app_label=app_config.get_app_label(),
                    defaults={"model": models.__name__},
                )
        return True


class ContentType(AbstractContentType):
    class Meta:
        unique_together = [["app_label", "model"]]
        tablename = "edgy_guardian_contenttypes"
