import bot.types
import pyrogram.types
from typing import Any


class CallbackQuery(pyrogram.types.CallbackQuery):
    message: bot.types.Message

    def __init__(self, client: "bot.Bot", **kwargs: Any) -> None:
        super().__init__(client=client, **kwargs)
