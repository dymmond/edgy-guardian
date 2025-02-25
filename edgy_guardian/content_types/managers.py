from __future__ import annotations

from typing import Any

import edgy


class ContentTypeManager(edgy.Manager):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._cache = {}

    async def get_by_natural_key(self, app_label: str, model: str) -> Any:
        """
        Asynchronously retrieves a content type by its natural key (app_label and model).

        Args:
            app_label (str): The label of the application.
            model (str): The name of the model.
        Returns:
            Any: The content type instance corresponding to the given app_label and model.
        Raises:
            KeyError: If the content type is not found in the cache.
        """

        try:
            ctype = self._cache[self.owner.database][(app_label, model)]
        except KeyError:
            ctype = await self.get(app_label=app_label, model=model)
            self._add_to_cache(self.owner.database, ctype)
        return ctype

    def _get_opts(self, model: edgy.Model) -> Any:
        """
        Retrieve the meta options for a given model.

        Args:
            model (edgy.Model): The model instance from which to retrieve meta options.
        Returns:
            Any: The meta options of the given model.
        """

        return model.meta

    def _get_from_cache(self, opts):
        """
        Retrieve an item from the cache based on the given options.
        Args:
            opts: An object containing the app_label and model_name attributes.
        Returns:
            The cached item corresponding to the given app_label and model_name.
        Raises:
            KeyError: If the item is not found in the cache.
        """
        key = (opts.app_label, opts.model_name)
        return self._cache[self.owner.database][key]

    async def get_for_model(self, model: str) -> type[edgy.Model]:
        """
        Retrieve the ContentType instance for the given model name.

        Args:
            model (str): The model name.
        Returns:
            ContentType: The ContentType instance.
        """
        return await self.get(model=model.meta.tablename)

    async def get_for_id(self, id: Any) -> tuple[str, str]:
        """
        Asynchronously retrieves the content type for the given ID.
        This method first attempts to retrieve the content type from the cache.
        If the content type is not found in the cache, it fetches it from the database
        and adds it to the cache.

        Args:
            id (Any): The ID of the content type to retrieve.
        Returns:
            tuple[str, str]: The content type associated with the given ID.
        """

        try:
            ctype = self._cache[self.owner.database][id]
        except KeyError:
            ctype = await self.get(pk=id)
            self._add_to_cache(self.owner.database, ctype)
        return ctype

    def clear_cache(self) -> None:
        """
        Clears the cache by removing all items from the internal cache dictionary.
        This method is used to reset the cache, ensuring that any previously stored
        data is removed and the cache is empty.
        """
        self._cache.clear()

    def _add_to_cache(self, using: Any, ctype: Any) -> None:
        """
        Adds a content type object to the cache.
        This method stores the given content type object in the cache, indexed by both
        its (app_label, model) tuple and its ID.

        Args:
            using (Any): The database alias being used.
            ctype (Any): The content type object to be cached.
        Returns:
            None
        """

        key = (ctype.app_label, ctype.model)
        self._cache.setdefault(using, {})[key] = ctype
        self._cache.setdefault(using, {})[ctype.id] = ctype
