from enum import Enum


class DefaultEnum(str, Enum):
    USER_DEFAULT = "User"
    GROUP_DEFAULT = "Group"
    PERMISSION_DEFAULT = "Permission"
    CONTENT_TYPE_DEFAULT = "ContentType"

    def __str__(self) -> str:
        return self.value

    def __repr__(self):
        return str(self)
