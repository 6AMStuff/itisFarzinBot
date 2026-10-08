from typing import TYPE_CHECKING, Any

import pyrogram.types

if TYPE_CHECKING:
    import itisfarzinbot


class CallbackQuery(pyrogram.types.CallbackQuery):
    message: "itisfarzinbot.types.Message | None"  # type: ignore[assignment]

    def __init__(self, client: "itisfarzinbot.Bot", **kwargs: Any) -> None:
        super().__init__(client=client, **kwargs)
