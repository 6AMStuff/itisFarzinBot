import logging
from pathlib import Path
from typing import Generator
from importlib import import_module

from pyrogram import Client
from pyrogram.handlers.handler import Handler


class Bot(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_plugins(folder="bot/builtin_plugins")

    def plugin_list(
        self, folder: str = None, only_name: bool = True
    ) -> list[str | Path]:
        return sorted([
            path.stem if only_name else path
            for path in Path(
                (folder or self.plugins["root"]).replace(".", "/")
            ).rglob("*.py")
        ])

    def get_handlers(
        self, plugins: str | list[str], folder: str = None
    ) -> Generator[tuple[str, str] | tuple[Handler, int], None, None]:
        if isinstance(plugins, str):
            plugins = plugins.split(",")

        _plugins = self.plugin_list(folder=folder)

        if plugins:
            for plugin in plugins:
                if plugin not in _plugins:
                    yield (plugin, "Plugin not found")

        for path in self.plugin_list(folder=folder, only_name=False):
            if path.stem not in (plugins or _plugins):
                continue

            module_path = '.'.join(path.parent.parts + (path.stem,))
            module = import_module(module_path)

            for name in vars(module).keys():
                target_attr = getattr(module, name)
                if hasattr(target_attr, "handlers"):
                    for handler, group in target_attr.handlers:
                        if (
                            isinstance(handler, Handler)
                            and isinstance(group, int)
                        ):
                            yield (handler, group)

    def is_loaded(self, handler: Handler, group: int = 0) -> bool:
        if group not in self.dispatcher.groups:
            return False
        return handler in self.dispatcher.groups[group]

    def load_plugins(
        self, plugins: str | list[str] = None, folder: str = None
    ) -> dict[str, str]:
        result = {}

        for handler in self.get_handlers(plugins, folder=folder):
            if isinstance(handler[0], str):
                result[handler[0]] = handler[1]
                logging.warning(handler[1])
            else:
                callback_name = handler[0].callback.__name__
                if not self.is_loaded(*handler):
                    self.add_handler(*handler)
                    result[callback_name] = "Handler loaded"
                    logging.info(f"{callback_name} handler has been loaded")
                else:
                    result[callback_name] = "Failed to load handler"
                    logging.warning(
                        f"Failed to load {callback_name} handler, "
                        "because it is already loaded"
                    )
        return result

    def unload_plugins(
        self, plugins: str | list[str] = None, folder: str = None
    ):
        result = {}

        for handler in self.get_handlers(plugins, folder=folder):
            if isinstance(handler[0], str):
                result[handler[0]] = handler[1]
                logging.warning(handler[1])
            else:
                callback_name = handler[0].callback.__name__
                if self.is_loaded(*handler):
                    self.remove_handler(*handler)
                    result[callback_name] = "Handler unloaded"
                    logging.info(f"{callback_name} handler has been unloaded")
                else:
                    result[callback_name] = "Failed to unload handler"
                    logging.warning(
                        f"Failed to unload {callback_name} handler, "
                        "it is not loaded already."
                    )
        return result
