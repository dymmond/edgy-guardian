from typing import Any, cast

import edgy


class ContentTypeManager(edgy.Manager):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._cache: dict[Any, Any] = {}

    async def get_for_model(self, model: str | type[edgy.Model]) -> type[edgy.Model]:
        """
        Retrieve the ContentType instance for the given model name.

        Args:
            model (str): The model name.
        Returns:
            ContentType: The ContentType instance.
        """
        if isinstance(model, edgy.Model):
            return cast(type[edgy.Model], await self.get(model=model.meta.tablename))  # type: ignore
        return cast(type[edgy.Model], await self.get(model=model))

    async def get_for_id(self, id: Any) -> Any:
        """
        Asynchronously retrieves the content type for the given ID.
        This method first attempts to retrieve the content type from the cache.
        If the content type is not found in the cache, it fetches it from the database
        and adds it to the cache.

        Args:
            id (Any): The ID of the content type to retrieve.
        Returns:
            Any: The content type associated with the given ID.
        """

        try:
            ctype = self._cache[id][id]
        except KeyError:
            ctype = await self.get(pk=id)
            self._add_to_cache(ctype.id, ctype)
        return ctype

    def clear_cache(self) -> None:
        """
        Clears the cache by removing all items from the internal cache dictionary.
        This method is used to reset the cache, ensuring that any previously stored
        data is removed and the cache is empty.
        """
        self._cache.clear()

    def _add_to_cache(self, key: Any, ctype: Any) -> None:
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
        base = key
        key = (ctype.app_label, ctype.model)
        self._cache.setdefault(base, {})[key] = ctype
        self._cache.setdefault(base, {})[ctype.id] = ctype
