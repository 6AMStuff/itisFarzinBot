from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyrogram.types import *  # pyright: ignore # noqa: F403

    from .callback_query import CallbackQuery as CallbackQuery
    from .message import Message as Message
else:
    import sys

    import pyrogram.types as pg_types

    from .callback_query import CallbackQuery as _CallbackQuery
    from .message import Message as _Message

    _current_module = sys.modules[__name__]
    for _name in dir(pg_types):
        if not _name.startswith("_"):
            setattr(_current_module, _name, getattr(pg_types, _name))

    _current_module.CallbackQuery = _CallbackQuery
    _current_module.Message = _Message
