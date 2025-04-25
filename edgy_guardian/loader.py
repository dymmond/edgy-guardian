import logging
from typing import TYPE_CHECKING, Any

from edgy.conf import settings

from edgy_guardian.exceptions import GuardianImproperlyConfigured
from edgy_guardian.utils import get_content_type_model

if TYPE_CHECKING:
    from edgy_guardian.content_types.models import BaseContentType

logger = logging.getLogger(__name__)


async def handle_content_types() -> None:
    """
    Manages the content types of the application.

    This function is used to manage the content types of the application.
    It creates the content types for all the models that are registered
    with the application.

    This function **must be run** before any other operation that
    involves content types or permissions.

    Usually, using a lifespan event is the best way to run this function.
    """
    from edgy_guardian.apps import get_apps

    try:
        existing_content_types: list[
            BaseContentType
        ] = await get_content_type_model().guardian.all()
    except KeyError:
        raise GuardianImproperlyConfigured(
            "EdgyGuardian requires a `content types` app/model to be installed and it seems that it is not installed or it was accidentally removed."
        ) from None

    deleted_apps: dict[str, Any] = {}
    for ctype in existing_content_types:
        if ctype.model_class() not in settings.edgy_guardian.registry.models.values():
            if ctype.app_label not in deleted_apps:
                deleted_apps[ctype.app_label] = []
            deleted_apps[ctype.app_label].append(ctype.model)

    models = set()
    new_apps: dict[str, Any] = {}
    for name, app_config in get_apps().app_configs.items():
        for _, model_class in app_config.get_models().items():
            if name not in deleted_apps:
                if name not in new_apps:
                    new_apps[name] = []
                if model_class.meta.tablename in models:
                    continue
                models.add(model_class.meta.tablename)
                new_apps[name].append(model_class.meta.tablename)

    for name, models in deleted_apps.items():
        for model in models:
            await get_content_type_model().guardian.filter(app_label=name, model=model).delete()

    for name, models in new_apps.items():
        for model in models:
            await get_content_type_model().guardian.get_or_create(app_label=name, model=model)

    logger.info("Content types have been successfully managed.")
