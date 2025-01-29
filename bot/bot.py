import logging
from glob import glob
from importlib import import_module, util

from pyrogram import Client
from pyrogram.handlers.handler import Handler


class Bot(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_plugins(path="bot/builtin_plugins")

    def plugin_list(self, path: str = None):
        return sorted([
            name.split(".py")[0]
            for name in glob("*.py", root_dir=path or self.plugins["root"])
        ])

    def does_plugin_exist(self, plugin: str, path: str = None):
        module_path = (
            path and path.replace("/", ".") or self.plugins["root"]
        ) + "." + plugin
        return bool(util.find_spec(module_path))

    def get_handlers(self, plugins: str | list[str], path: str = None):
        if isinstance(plugins, str):
            plugins = plugins.split(",")

        for pname in plugins:
            path = path and path.replace("/", ".") or self.plugins["root"]
            module_path = path + "." + pname

            if not self.does_plugin_exist(pname, path):
                yield (pname, "Plugin not found")
                continue
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

    def is_loaded(self, handler: Handler, group: int = 0):
        if group not in self.dispatcher.groups:
            return False
        return handler in self.dispatcher.groups[group]

    def load_plugins(self, plugins: str | list[str] = None, path: str = None):
        result = {}

        for handler in self.get_handlers(
            plugins or self.plugin_list(path=path),
            path=path
        ):
            if isinstance(handler[1], str):
                result[handler[0]] = handler[1]
                logging.warning(handler[1])
            elif not self.is_loaded(*handler):
                self.add_handler(*handler)
                result[handler[0].callback.__name__] = "Loaded"
                logging.info(f"Loaded: {handler[0].callback.__name__}")
            else:
                result[handler[0].callback.__name__] = "Failed to load"
                logging.warning(
                    f"Failed to load: {handler[0].callback.__name__}, "
                    "already loaded"
                )
        return result

    def unload_plugins(
        self, plugins: str | list[str] = None, path: str = None
    ):
        result = {}

        for handler in self.get_handlers(
            plugins or self.plugin_list(path=path)
        ):
            if isinstance(handler[1], str):
                result[handler[0]] = handler[1]
                logging.warning(handler[1])
            elif self.is_loaded(*handler):
                self.remove_handler(*handler)
                result[handler[0].callback.__name__] = "Unloaded"
                logging.info(f"Unloaded: {handler[0].callback.__name__}")
            else:
                result[handler[0].callback.__name__] = "Failed to unload"
                logging.warning(
                    f"Failed to unload: {handler[0].callback.__name__}, "
                    "not loaded already"
                )
        return result
