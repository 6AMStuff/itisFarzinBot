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
        self, handler, parsed_update, update, users, chats, handler_type
    ):
        args = await self.get_handler_args(
            handler, parsed_update, update, users, chats, handler_type
        )

        if not args:
            return False

        return await self.invoke_handler(handler, args)

    async def get_handler_args(
        self, handler, parsed_update, update, users, chats, handler_type
    ):
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
            return False
        except Exception as e:
            logging.exception(e)

        return True
