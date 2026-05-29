import shlex
from typing import TYPE_CHECKING, Any

import pyrogram.types

if TYPE_CHECKING:
    import bot


class Message(pyrogram.types.Message):
    def __init__(self, client: "bot.Bot", **kwargs: Any) -> None:
        super().__init__(client=client, **kwargs)

    def parse_arguments(self) -> dict[str, Any]:
        # Limit it to filter.command
        if not self.command:
            return {}

        raw = self.content.split(maxsplit=1)
        if len(raw) < 2:
            return {}

        tokens = shlex.split(raw[1])
        arguments: dict[str, Any] = {}

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
