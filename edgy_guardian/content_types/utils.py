from typing import Any, cast

import edgy

from edgy_guardian.utils import get_content_type_model


async def get_content_type(obj: Any) -> type[edgy.Model]:
    """
    Returns the default content type for the given object.

    Parameters
    ----------
    obj : Any
        The object for which the content type is to be retrieved.

    Returns
    -------
    ContentType
        The content type of the object.
    """
    return cast(type[edgy.Model], await get_content_type_model().guardian.get_for_model(obj))
