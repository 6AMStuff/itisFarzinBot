import inspect
import logging
import pyrogram.handlers
import pyrogram.dispatcher

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import bot


class Dispatcher(pyrogram.dispatcher.Dispatcher):
    def __init__(self, client: "bot.Bot"):
        super().__init__(client)

    async def handler_worker(self, lock):
        while True:
            packet = await self.updates_queue.get()

            if packet is None:
                break

            try:
                await self.process_packet(packet, lock)
            except pyrogram.StopPropagation:
                pass
            except Exception as e:
                logging.exception(e)

    async def process_packet(self, packet, lock):
        update, users, chats = packet
        parser = self.update_parsers.get(type(update), None)

        parsed_update, handler_type = (
            await parser(update, users, chats)
            if parser is not None
            else (None, type(None))
        )

        async with lock:
            for group in self.groups.values():
                for handler in group:
                    await self.process_handler(
                        handler,
                        parsed_update,
                        update,
                        users,
                        chats,
                        handler_type,
                    )
                    break

    async def process_handler(
        self, handler, parsed_update, update, users, chats, handler_type
    ):
        if isinstance(handler, handler_type):
            args = await self.get_args_for_parsed_update(
                handler, parsed_update
            )
        elif isinstance(
            handler, pyrogram.handlers.raw_update_handler.RawUpdateHandler
        ):
            args = await self.get_args_for_raw_update(
                handler, update, users, chats
            )
        else:
            return

        if args is not None:
            await self.invoke_handler(handler, args)

    async def get_args_for_parsed_update(self, handler, parsed_update):
        try:
            if await handler.check(self.client, parsed_update):
                return (parsed_update,)
        except Exception as e:
            logging.exception(e)

        return None

    async def get_args_for_raw_update(self, handler, update, users, chats):
        try:
            if await handler.check(self.client, update):
                return (update, users, chats)
        except Exception as e:
            logging.exception(e)

        return None

    async def invoke_handler(self, handler, args):
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
            return
        except Exception as e:
            logging.exception(e)
