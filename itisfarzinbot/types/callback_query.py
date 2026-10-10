from typing import TYPE_CHECKING

import pyrogram.types

if TYPE_CHECKING:
    import itisfarzinbot
    import itisfarzinbot.types


class CallbackQuery(pyrogram.types.CallbackQuery):
    # Override to use our custom Message type
    message: "itisfarzinbot.types.Message | None"  # type: ignore[assignment]

    def __init__(self, client: "itisfarzinbot.Bot", **kwargs: object) -> None:
        super().__init__(client=client, **kwargs)  # type: ignore[arg-type]
