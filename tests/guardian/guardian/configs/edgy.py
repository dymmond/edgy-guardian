from edgy import EdgySettings as BaseSettings

from edgy_guardian.configs import EdgyGuardianConfig


class EdgyAppSettings(BaseSettings):
    preloads: list[str] = [
        "accounts.models",
        "permissions.models",
        "contenttypes.models",
        "products.models",
        "items.models",
    ]
    edgy_guardian: EdgyGuardianConfig = EdgyGuardianConfig(
        models={
            "accounts": "accounts.models",
            "contenttypes": "contenttypes.models",
            "permissions": "permissions.models",
            "products": "products.models",
            "items": "items.models",
        },
        apps=[
            "accounts.apps.AccountsConfig",
            "permissions.apps.PermissionsConfig",
            "contenttypes.apps.ContentTypesConfig",
            "products.apps.ProductsConfig",
            "items.apps.ItemsConfig",
        ],
        content_type_model="ContentType",
        user_model="User",
        permission_model="Permission",
        group_model="Group",
    )
