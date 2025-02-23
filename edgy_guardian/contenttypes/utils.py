from typing import Any

from edgy_guardian.contenttypes.models import ContentType


async def get_content_type(obj: Any) -> ContentType:
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
    return await ContentType.query.get_for_model(obj)
