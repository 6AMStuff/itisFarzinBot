import shlex
from typing import TYPE_CHECKING

import pyrogram.types

if TYPE_CHECKING:
    import itisfarzinbot


class Message(pyrogram.types.Message):
    def __init__(self, client: "itisfarzinbot.Bot", **kwargs: object) -> None:
        super().__init__(client=client, **kwargs)  # type: ignore[arg-type]

    def parse_arguments(self) -> dict[str, object]:
        # Limit it to filter.command
        if self.command is None or len(self.command) == 0:
            return {}

        raw = self.content.split(maxsplit=1)
        if len(raw) < 2:
            return {}

        tokens = shlex.split(raw[1])
        arguments: dict[str, object] = {}

        i = 0

        while i < len(tokens):
            token = tokens[i]

            if not token.startswith("-"):
                i += 1
                continue

            key = token.lstrip("-")

            if i + 1 >= len(tokens) or tokens[i + 1].startswith("-"):
                arguments[key] = True
                i += 1
                continue

            arguments[key] = tokens[i + 1]
            i += 2

        return arguments
