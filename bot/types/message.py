import pyrogram.types

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import bot


class Message(pyrogram.types.Message):
    def __init__(self, client: "bot.Bot", **kwargs):
        super().__init__(client=client, **kwargs)
