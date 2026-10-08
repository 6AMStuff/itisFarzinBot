from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyrogram.types import *  # pyright: ignore # noqa: F403

    from .callback_query import (  # type: ignore[assignment]
        CallbackQuery as CallbackQuery,
    )
    from .message import Message as Message  # type: ignore[assignment]
else:
    import sys

    import pyrogram.types as pg_types

    from .callback_query import CallbackQuery
    from .message import Message

    _current_module = sys.modules[__name__]
    for _name in dir(pg_types):
        if not _name.startswith("_"):
            setattr(_current_module, _name, getattr(pg_types, _name))

    _current_module.CallbackQuery = CallbackQuery
    _current_module.Message = Message
