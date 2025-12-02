import os
import logging
import importlib
from pathlib import Path
from pyrogram import Client
from sqlalchemy import select
from sqlalchemy.orm import Session
from pyrogram.handlers.handler import Handler
from typing import Generator, Optional, Iterator
from settings import Settings, DataBase, PluginDatabase


class PluginManager(Client):
    plugins: dict
    builtin_plugin: str

    def _post_init(self):
        self.load_plugins(folder=self.builtin_plugin)

    def modules_list(
        self, folder: Optional[str | list[str]] = None
    ) -> Iterator[Path]:
        targets = (
            folder
            if isinstance(folder, list)
            else [folder or self.plugins["root"]]
        )

        for path_str in targets:
            for root, _, files in os.walk(
                path_str.replace(".", os.sep), followlinks=True
            ):
                for file in files:
                    if file.endswith(".py"):
                        yield Path(root) / file

    def get_plugins(
        self, folder: Optional[str | list[str]] = None
    ) -> list[str] | list[Path]:
        plugins = []

        folders = (
            folder
            if isinstance(folder, list)
            else [folder or self.plugins["root"]]
        )

        for path in self.modules_list(folders):
            module_path = ".".join(path.with_suffix("").parts)
            module = importlib.import_module(module_path)
            if getattr(module, "__plugin__", False):
                plugins.append(path.stem)

        return sorted(plugins)

    def get_handlers(
        self,
        plugins: Optional[str | list[str]] = None,
        folder: Optional[str | list[str]] = None,
    ) -> Generator[tuple[str, str] | tuple[Handler, int], None, None]:
        if isinstance(plugins, str):
            plugins = plugins.split(",")

        group_offset = 0 if folder == self.builtin_plugin else 1
        _plugins = self.get_plugins(folder=folder)

        if plugins:
            for plugin in plugins:
                if plugin not in _plugins:
                    yield (plugin, "Plugin not found")

        for path in self.modules_list(folder=folder):
            if plugins and path.stem not in plugins:
                continue

            module_path = ".".join(path.parent.parts + (path.stem,))
            module = importlib.import_module(module_path)
            # TODO: reload the module after import

            for name in vars(module).keys():
                if handlers := getattr(
                    getattr(module, name), "handlers", None
                ):
                    if not isinstance(handlers, list):
                        continue

                    for handler, group in handlers:
                        if isinstance(handler, Handler) and isinstance(
                            group, int
                        ):
                            if group < 0 and group_offset != 0:
                                yield (handler, 0)
                            else:
                                yield (handler, group + group_offset)

    def handler_is_loaded(self, handler: Handler, group: int = 0) -> bool:
        if group not in self.dispatcher.groups:
            return False
        return handler in self.dispatcher.groups[group]

    def set_plugin_status(self, plugin: str, enabled: bool = True):
        with Session(Settings.engine) as session:
            session.merge(PluginDatabase(name=plugin, enabled=enabled))
            session.commit()

    def get_plugin_status(self, plugin: str) -> bool:
        with Session(Settings.engine) as session:
            enabled = session.execute(
                select(PluginDatabase.enabled).where(
                    PluginDatabase.name == plugin
                )
            ).scalar()
            return enabled or False

    def load_plugins(
        self,
        plugins: Optional[str | list[str]] = None,
        folder: Optional[str | list[str]] = None,
        force_load: bool = False,
    ) -> dict[str, str]:
        result = {}
        plugins: set[str] = set(
            plugins.split(",") if isinstance(plugins, str) else plugins or ""
        )
        all_plugins = set(self.get_plugins(folder=folder))
        plugins = plugins or all_plugins
        valid_plugins = plugins.intersection(all_plugins)
        disabled_plugins = set()

        if not force_load:
            with Session(Settings.engine) as session:
                stmt = select(PluginDatabase.name).where(
                    PluginDatabase.name.in_(plugins),
                    PluginDatabase.enabled.is_(False)
                )
                disabled_plugins = set(session.execute(stmt).scalars().all())

        for plugin in valid_plugins:
            if plugin in disabled_plugins:
                plugins.discard(plugin)
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

        DataBase.metadata.create_all(Settings.engine)
        return result

    def unload_plugins(
        self,
        plugins: Optional[str | list[str]] = None,
        folder: Optional[str | list[str]] = None,
    ):
        result = {}
        if isinstance(plugins, str):
            plugins = plugins.split(",")

        _plugins = self.get_plugins(folder=folder)
        plugins = plugins or _plugins

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
