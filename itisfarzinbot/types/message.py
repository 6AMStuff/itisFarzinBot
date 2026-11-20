import shlex
from typing import TYPE_CHECKING

import pyrogram.types
from sqlalchemy.orm import Session

from itisfarzinbot.settings import AdminDatabase, Settings

if TYPE_CHECKING:
    import itisfarzinbot


class Message(pyrogram.types.Message):
    def __init__(self, client: "itisfarzinbot.Bot", **kwargs: object) -> None:
        super().__init__(client=client, **kwargs)  # type: ignore[arg-type]

    @property
    def is_admin(self) -> bool:
        user = self.from_user
        if user is None:
            return False

        if user.username is not None and f"@{user.username.lower()}" in (
            admin.lower() for admin in Settings.ADMINS
        ):
            return True

        with Session(Settings.engine) as session:
            return session.get(AdminDatabase, user.id) is not None

    def parse_arguments(self) -> dict[str, object]:
        # Limit it to filter.command
        if self.command is None or len(self.command) == 0:
            return {}

        raw = self.content.split(maxsplit=1)
        if len(raw) < 2:
            return {}

        try:
            tokens = shlex.split(raw[1])
        except ValueError:
            return {}

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
