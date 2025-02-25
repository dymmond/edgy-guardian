from __future__ import annotations

from typing import Any

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
    return await get_content_type_model().query.get_for_model(obj)
