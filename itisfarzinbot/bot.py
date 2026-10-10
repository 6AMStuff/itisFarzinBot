import time
from typing import override

from pyrogram.client import Client

from itisfarzinbot.settings import DataBase, Settings

from .core import Core, Dispatcher


class BotMeta(type):
    def __call__(cls, *args: object, **kwargs: object) -> "Bot":
        instance: Bot = super().__call__(*args, **kwargs)
        instance._post_init()
        return instance


class Bot(Core, Client, metaclass=BotMeta):
    uptime: float
    is_bot: bool

    @override
    def _post_init(self) -> None:
        self.builtin_plugins = "itisfarzinbot/plugins"
        self.uptime = time.time()
        self.is_bot = bool(self.bot_token)
        self.dispatcher = Dispatcher(self)
        DataBase.metadata.create_all(Settings.engine)

        super()._post_init()
