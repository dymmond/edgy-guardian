from typing import Any

from esmerald.core.directives import BaseDirective


class Directive(BaseDirective):
    help = "Cleans the orphan permission objects from the system"

    async def handle(self, *args: Any, **options: Any) -> Any:
        ...
