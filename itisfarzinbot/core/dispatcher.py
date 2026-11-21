import functools
import inspect
import weakref
from collections.abc import Awaitable, Callable
from typing import TypeVar, override

import pyrogram.dispatcher
import pyrogram.handlers
import pyrogram.types

import itisfarzinbot.types

_Callback = Callable[..., object]
_ParsedUpdate = tuple[object, object]
_Parser = TypeVar("_Parser", bound=Callable[..., Awaitable[_ParsedUpdate]])
_ADAPTED: weakref.WeakSet[_Callback] = weakref.WeakSet()


def _set_custom_types(parsed: object) -> None:
    if isinstance(parsed, pyrogram.types.Message):
        parsed.__class__ = itisfarzinbot.types.Message
        reply = parsed.reply_to_message
        if isinstance(reply, pyrogram.types.Message):
            reply.__class__ = itisfarzinbot.types.Message

    elif isinstance(parsed, pyrogram.types.CallbackQuery):
        parsed.__class__ = itisfarzinbot.types.CallbackQuery
        if isinstance(parsed.message, pyrogram.types.Message):
            parsed.message.__class__ = itisfarzinbot.types.Message


def _custom_types(parser: _Parser) -> _Parser:
    @functools.wraps(parser)
    async def wrapped(*args: object, **kwargs: object) -> _ParsedUpdate:
        parsed, handler_type = await parser(*args, **kwargs)
        _set_custom_types(parsed)

        return parsed, handler_type

    return wrapped  # type: ignore[return-value]


def _clientless(callback: _Callback) -> _Callback:
    if inspect.iscoroutinefunction(callback):

        @functools.wraps(callback)
        async def async_adapted(_client: object, update: object) -> object:
            return await callback(update)

        return async_adapted

    @functools.wraps(callback)
    def sync_adapted(_client: object, update: object) -> object:
        return callback(update)

    return sync_adapted


class Dispatcher(pyrogram.dispatcher.Dispatcher):
    def __init__(self, client: "itisfarzinbot.Bot") -> None:
        super().__init__(client)

        self.update_parsers = {  # type: ignore[bad-assignment]
            update_type: _custom_types(parser)
            for update_type, parser in self.update_parsers.items()
        }

    @override
    def add_handler(
        self,
        handler: pyrogram.handlers.handler.Handler[_Callback],
        group: int,
    ) -> None:
        callback = handler.callback
        params = inspect.signature(callback).parameters
        if len(params) == 1 and callback not in _ADAPTED:
            adapted = _clientless(callback)
            _ADAPTED.add(adapted)
            handler.callback = adapted

        super().add_handler(handler, group)
