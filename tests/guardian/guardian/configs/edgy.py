from edgy import EdgySettings as BaseSettings

from edgy_guardian.configs import EdgyGuardianConfig


class EdgyAppSettings(BaseSettings):
    preloads: list[str] = [
        "accounts.models",
        "permissions.models",
        "contenttypes.models",
    ]
    edgy_guardian: EdgyGuardianConfig = EdgyGuardianConfig(
        models={
            "accounts": "accounts.models",
            "contenttypes": "contenttypes.models",
            "permissions": "permissions.models",
        },
        apps=[
            "accounts.apps.AccountsConfig",
            "permissions.apps.PermissionsConfig",
            "contenttypes.apps.ContentTypesConfig",
        ],
        content_type_model="guardian.apps.contenttypes.models.ContentType",
        user_model="guardian.apps.accounts.models.User",
        permission_model="guardian.apps.permissions.models.Permission",
        group_model="guardian.apps.permissions.models.Group",
    )
