from __future__ import annotations

from accounts.models import User
from edgy.testing.factory import FactoryField, ModelFactory
from items.models import Item
from products.models import Product


class UserFactory(ModelFactory):
    class Meta:
        model = User

    username = FactoryField(
        callback=lambda field, context, parameters: f"username-{field.get_callcount()}"
    )
    email = FactoryField(
        callback=lambda field, context, parameters: f"testuser-{field.get_callcount()}@edgy.com"
    )


class ItemFactory(ModelFactory):
    class Meta:
        model = Item

    name = FactoryField(
        callback=lambda field, context, parameters: f"item-{field.get_callcount()}"
    )
    description = FactoryField(
        callback=lambda field, context, parameters: f"description-{field.get_callcount()}"
    )


class ProductFactory(ModelFactory):
    class Meta:
        model = Product

    name = FactoryField(
        callback=lambda field, context, parameters: f"product-{field.get_callcount()}"
    )
    description = FactoryField(
        callback=lambda field, context, parameters: f"description-{field.get_callcount()}"
    )
