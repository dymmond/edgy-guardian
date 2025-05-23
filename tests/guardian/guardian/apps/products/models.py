import edgy
from esmerald.conf import settings


class Product(edgy.Model):
    name: str = edgy.CharField(max_length=255)
    description: str = edgy.TextField()

    class Meta:
        registry = settings.registry
