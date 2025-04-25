from enum import Enum


class DefaultEnum(str, Enum):
    USER_DEFAULT = "User"
    GROUP_DEFAULT = "Group"
    PERMISSION_DEFAULT = "Permission"
    CONTENT_TYPE_DEFAULT = "ContentType"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)


class UserGroup(str, Enum):
    USER = "users"
    GROUP = "groups"
    PERMISSIONS = "permissions"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)
