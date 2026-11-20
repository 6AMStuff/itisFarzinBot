import asyncio
import inspect
import logging
from collections.abc import Awaitable, Callable
from typing import cast, override

import pyrogram.dispatcher
import pyrogram.handlers
import pyrogram.types

import itisfarzinbot
import itisfarzinbot.types


class Dispatcher(pyrogram.dispatcher.Dispatcher):
    @override
    async def handler_worker(self) -> None:
        while True:
            packet = await self.updates_queue.get()

            if not isinstance(packet, tuple):
                break

            try:
                await self.process_packet(packet)
            except pyrogram.StopPropagation:
                pass
            except Exception as e:
                logging.exception(e)

    async def process_packet(
        self,
        packet: tuple[
            pyrogram.raw.base.update.Update,
            dict[int, pyrogram.raw.base.user.User],
            dict[int, pyrogram.raw.base.chat.Chat],
        ],
    ) -> None:
        update, users, chats = packet
        parser = self.update_parsers.get(type(update), None)  # type: ignore[call-overload]

        if parser is None:
            return

        parsed_update, handler_type = await parser(update, users, chats)

        if not isinstance(
            parsed_update, pyrogram.types.Update
        ) or not isinstance(
            handler_type, type(pyrogram.handlers.handler.Handler)
        ):
            return

        for group in self._copy_groups().values():
            for handler in group:
                if await self.process_handler(
                    handler,
                    parsed_update,
                    update,
                    users,
                    chats,
                    handler_type,
                ):
                    break

    async def process_handler(
        self,
        handler: pyrogram.handlers.handler.Handler[Callable[..., object]],
        parsed_update: pyrogram.types.Update,
        update: pyrogram.raw.base.update.Update,
        users: dict[int, pyrogram.raw.base.user.User],
        chats: dict[int, pyrogram.raw.base.chat.Chat],
        handler_type: type[
            pyrogram.handlers.handler.Handler[Callable[..., object]]
        ],
    ) -> bool:
        args: (
            tuple[pyrogram.types.Update]
            | tuple[
                pyrogram.raw.base.update.Update,
                dict[int, pyrogram.raw.base.user.User],
                dict[int, pyrogram.raw.base.chat.Chat],
            ]
            | None
        ) = None
        try:
            if isinstance(handler, handler_type) and await handler.check(
                self.client, parsed_update
            ):
                args = (parsed_update,)
                self.set_custom_update_types(args[0])
            elif isinstance(
                handler, pyrogram.handlers.raw_update_handler.RawUpdateHandler
            ) and bool(await handler.check(self.client, update)):  # type: ignore[bad-argument-type]
                args = (update, users, chats)
        except Exception as e:
            logging.exception(e)

        if args is None:
            return False

        return await self.invoke_handler(handler, args)

    def set_custom_update_types(self, update: pyrogram.types.Update) -> None:
        if isinstance(update, pyrogram.types.Message):
            update.__class__ = itisfarzinbot.types.Message
            if update.reply_to_message is not None:
                update.reply_to_message.__class__ = itisfarzinbot.types.Message
        elif isinstance(update, pyrogram.types.CallbackQuery):
            update.__class__ = itisfarzinbot.types.CallbackQuery
            if isinstance(update.message, pyrogram.types.Message):
                update.message.__class__ = itisfarzinbot.types.Message

    async def invoke_handler(
        self,
        handler: pyrogram.handlers.handler.Handler[Callable[..., object]],
        args: tuple[object] | tuple[object, object, object],
    ) -> bool:
        sig = inspect.signature(handler.callback)
        custom_args = (
            args if len(sig.parameters) == 1 else (self.client, *args)
        )

        try:
            if inspect.iscoroutinefunction(handler.callback):
                await cast("Awaitable[object]", handler.callback(*custom_args))
            else:
                await asyncio.get_running_loop().run_in_executor(
                    self.client.executor,
                    handler.callback,
                    *custom_args,
                )
        except pyrogram.StopPropagation:
            raise
        except pyrogram.ContinuePropagation:
            return False
        except Exception as e:
            logging.exception(e)

        return True
