from typing import TYPE_CHECKING, Any

import pyrogram.types

if TYPE_CHECKING:
    import bot.types


class CallbackQuery(pyrogram.types.CallbackQuery):
    message: "bot.types.Message | None"  # type: ignore[assignment]

    def __init__(self, client: "bot.Bot", **kwargs: Any) -> None:
        super().__init__(client=client, **kwargs)
