import time
from .core import Core, Dispatcher
from pyrogram.client import Client
from bot.settings import Settings, DataBase


class BotMeta(type):
    def __call__(cls, *args, **kwargs):
        instance: Bot = super().__call__(*args, **kwargs)
        instance._post_init()
        return instance


class Bot(Core, Client, metaclass=BotMeta):
    def _post_init(self):
        self.builtin_plugin = "bot/builtin_plugins"
        self.uptime = time.time()
        self.is_bot = bool(self.bot_token)
        self.dispatcher = Dispatcher(self)
        DataBase.metadata.create_all(Settings.engine)

        for base_class in reversed(self.__class__.__bases__[0].__bases__):
            if base_class is self.__class__ or base_class is object:
                continue

            if hasattr(base_class, "_post_init"):
                _post_init = base_class._post_init
                if callable(_post_init):
                    _post_init(self)
