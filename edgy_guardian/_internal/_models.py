from typing import Any

import edgy


class BaseGuardianModel(edgy.Model):
    def __hash__(self) -> int:
        values: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            values[key] = None
            if isinstance(value, (list, set)):
                values[key] = tuple(value)
            else:
                values[key] = value
        return hash((type(self),) + tuple(values))
