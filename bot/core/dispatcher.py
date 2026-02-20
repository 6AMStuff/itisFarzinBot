import bot
import inspect
import logging
import asyncio
import bot.types
import pyrogram.types
from typing import Any
import pyrogram.handlers
import pyrogram.dispatcher


class Dispatcher(pyrogram.dispatcher.Dispatcher):
    def __init__(self, client: "bot.Bot"):
        super().__init__(client)

    async def handler_worker(self, lock: asyncio.locks.Lock) -> None:
        while True:
            packet = await self.updates_queue.get()

            if not isinstance(packet, tuple):
                break

            try:
                await self.process_packet(packet, lock)
            except pyrogram.StopPropagation:
                pass
            except Exception as e:
                logging.exception(e)

    async def process_packet(
        self,
        packet: tuple[Any, dict[int, Any], dict[Any, Any]],
        lock: asyncio.locks.Lock,
    ) -> None:
        update, users, chats = packet
        parser = self.update_parsers.get(type(update), None)  # type: ignore[call-overload]

        parsed_update, handler_type = (
            await parser(update, users, chats)
            if parser is not None
            else (None, type(None))
        )

        if not parsed_update or not isinstance(
            handler_type, type(pyrogram.handlers.handler.Handler)
        ):
            return

        async with lock:
            for group in self.groups.values():
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
        handler: pyrogram.handlers.handler.Handler,
        parsed_update: pyrogram.types.Update,
        update: Any,
        users: dict[int, pyrogram.raw.types.user.User],
        chats: dict[int, pyrogram.raw.types.chat.Chat],
        handler_type: type[pyrogram.handlers.handler.Handler],
    ) -> bool:
        args = await self.get_handler_args(
            handler, parsed_update, update, users, chats, handler_type
        )

        if not args:
            return False

        if isinstance(args[0], pyrogram.types.Message):
            args[0].__class__ = bot.types.Message
            if args[0].reply_to_message:
                args[0].reply_to_message.__class__ = bot.types.Message

        return await self.invoke_handler(handler, args)

    async def get_handler_args(
        self,
        handler: pyrogram.handlers.handler.Handler,
        parsed_update: pyrogram.types.Update,
        update: Any,
        users: dict[int, pyrogram.raw.types.user.User],
        chats: dict[int, pyrogram.raw.types.chat.Chat],
        handler_type: type[pyrogram.handlers.handler.Handler],
    ) -> tuple[Any] | tuple[Any, Any, Any] | None:
        try:
            if isinstance(handler, handler_type) and await handler.check(
                self.client, parsed_update
            ):
                return (parsed_update,)
            elif isinstance(
                handler, pyrogram.handlers.raw_update_handler.RawUpdateHandler
            ) and await handler.check(self.client, update):
                return (update, users, chats)
        except Exception as e:
            logging.exception(e)

        return None

    async def invoke_handler(
        self,
        handler: pyrogram.handlers.handler.Handler,
        args: tuple[Any] | tuple[Any, Any, Any],
    ) -> bool:
        try:
            if inspect.iscoroutinefunction(handler.callback):
                await handler.callback(self.client, *args)
            else:
                await self.client.loop.run_in_executor(
                    self.client.executor,
                    handler.callback,
                    self.client,
                    *args,
                )
        except pyrogram.StopPropagation:
            raise
        except pyrogram.ContinuePropagation:
            return False
        except Exception as e:
            logging.exception(e)

        return True
