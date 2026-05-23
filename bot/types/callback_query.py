import pyrogram.types
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    import bot


class CallbackQuery(pyrogram.types.CallbackQuery):
    def __init__(self, client: "bot.Bot", **kwargs: Any) -> None:
        super().__init__(client=client, **kwargs)
