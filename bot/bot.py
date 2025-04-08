import os
import logging
import importlib
from pathlib import Path
from pyrogram import Client
from typing import Generator
from sqlalchemy import select
from sqlalchemy.orm import Session
from pyrogram.handlers.handler import Handler
from config import Config, DataBase, PluginDatabase


class BotMeta(type):
    def __call__(cls, *args, **kwargs):
        instance: Bot = super().__call__(*args, **kwargs)
        instance._post_init()
        return instance


class Bot(Client, metaclass=BotMeta):
    def _post_init(self):
        self.builtin_plugin = "bot/builtin_plugins"
        DataBase.metadata.create_all(Config.engine)
        self.load_plugins(folder=self.builtin_plugin)

    def plugin_list(
        self,
        folder: str | list[str] = None,
        full_path: bool = False,
        with_non_plugins: bool = True,
        load: bool = True
    ) -> list[str | Path]:
        plugins = []

        folders = folder if isinstance(folder, list) else [
            folder or self.plugins["root"]
        ]

        for f in folders:
            for root, _, files in os.walk(
                f.replace(".", "/"),
                followlinks=True
            ):
                for file in files:
                    if not file.endswith(".py"):
                        continue
                    path = Path(root) / file
                    if load:
                        module_path = ".".join(
                            path.parent.parts + (path.stem,)
                        )
                        module = importlib.import_module(module_path)
                        if not with_non_plugins:
                            if not getattr(module, "__plugin__", False):
                                continue
                    plugins.append(path if full_path else path.stem)

        return sorted(plugins)

    def get_handlers(
        self, plugins: str | list[str], folder: str | list[str] = None,
    ) -> Generator[tuple[str, str] | tuple[Handler, int], None, None]:
        if isinstance(plugins, str):
            plugins = plugins.split(",")

        group_offset = 0 if folder == self.builtin_plugin else 1
        _plugins = self.plugin_list(folder=folder)
        if plugins is None:
            plugins = _plugins

        for plugin in plugins:
            if plugin not in _plugins:
                yield (plugin, "Plugin not found")

        for path in self.plugin_list(folder=folder, full_path=True):
            if path.stem not in plugins:
                continue

            module_path = '.'.join(path.parent.parts + (path.stem,))
            module = importlib.import_module(module_path)
            # TODO: reload the module after import

            for name in vars(module).keys():
                target_attr = getattr(module, name)
                if hasattr(target_attr, "handlers"):
                    for handler, group in target_attr.handlers:
                        if (
                            isinstance(handler, Handler)
                            and isinstance(group, int)
                        ):
                            yield (handler, group + group_offset)

    def handler_is_loaded(self, handler: Handler, group: int = 0) -> bool:
        if group not in self.dispatcher.groups:
            return False
        return handler in self.dispatcher.groups[group]

    def set_plugin_status(self, plugin: str, enabled: bool = True):
        with Session(Config.engine) as session:
            session.merge(PluginDatabase(name=plugin, enabled=enabled))
            session.commit()

    def load_plugins(
        self,
        plugins: str | list[str] = None,
        folder: str | list[str] = None,
        force_load: bool = False
    ) -> dict[str, str]:
        result = {}
        if isinstance(plugins, str):
            plugins = plugins.split(",")

        _plugins = self.plugin_list(folder=folder)
        if plugins is None:
            plugins = _plugins

        for plugin in plugins:
            if plugin in _plugins:
                with Session(Config.engine) as session:
                    if session.execute(
                        select(PluginDatabase.enabled)
                        .where(PluginDatabase.name == plugin)
                    ).scalar() is False and not force_load:
                        plugins.remove(plugin)
                    else:
                        self.set_plugin_status(plugin, True)

        for handler in self.get_handlers(plugins, folder=folder):
            if isinstance(handler[0], str):
                result[handler[0]] = handler[1]
                logging.warning(handler[1])
            else:
                callback_name = handler[0].callback.__name__
                if not self.handler_is_loaded(*handler):
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
        self, plugins: str | list[str] = None, folder: str | list[str] = None
    ):
        result = {}
        if isinstance(plugins, str):
            plugins = plugins.split(",")

        _plugins = self.plugin_list(folder=folder)
        if plugins is None:
            plugins = _plugins

        for plugin in plugins:
            if plugin in _plugins:
                self.set_plugin_status(plugin, False)

        for handler in self.get_handlers(plugins, folder=folder):
            if isinstance(handler[0], str):
                result[handler[0]] = handler[1]
                logging.warning(handler[1])
            else:
                callback_name = handler[0].callback.__name__
                if self.handler_is_loaded(*handler):
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
