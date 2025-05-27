import bot
import functools
from typing import Callable
from sqlalchemy import select
from sqlalchemy.orm import Session
from config import Config, PluginDatabase
from pyrogram.types import Message, InlineQuery


class IsPublicUse:
    def is_public_use(func: Callable):
        @functools.wraps(func)
        async def decorator(client: "bot.Bot", update: Message | InlineQuery):
            if await Config.IS_ADMIN(client, update):
                return await func(client, update)

            with Session(Config.engine) as session:
                if session.execute(
                    select(PluginDatabase.is_public_use).where(
                        PluginDatabase.name == func.__module__.split(".")[-1]
                    )
                ).scalar():
                    return await func(client, update)

            return None

        return decorator
