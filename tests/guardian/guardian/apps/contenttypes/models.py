from esmerald.conf import settings

from edgy_guardian.content_types.models import BaseContentType


class ContentType(BaseContentType):
    class Meta:
        registry = settings.registry
