import os
import logging
import inspect
import importlib
from pathlib import Path
from typing import Iterator
from sqlalchemy import select
from pyrogram.client import Client
from sqlalchemy.orm import Session
from pyrogram.handlers.handler import Handler
from bot.settings import Settings, DataBase, PluginDatabase


class PluginManager(Client):
    plugins: dict
    builtin_plugin: str

    def _post_init(self):
        self.custom_load_plugins(folder=self.builtin_plugin)

    def modules_list(
        self, folder: str | list[str] | set[str] | None = None
    ) -> Iterator[Path]:
        targets = (
            folder
            if isinstance(folder, (list, set))
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
        self, folder: str | list[str] | set[str] | None = None
    ) -> Iterator[str]:
        targets = (
            folder
            if isinstance(folder, (list, set))
            else [folder or self.plugins["root"]]
        )

        for path in self.modules_list(targets):
            module_path = ".".join(path.with_suffix("").parts)
            module = importlib.import_module(module_path)
            if getattr(module, "__plugin__", False):
                yield path.stem

    def get_handlers(
        self,
        plugins: str | list[str] | set[str] | None = None,
        folder: str | list[str] | set[str] | None = None,
    ) -> Iterator[tuple[Handler, int]]:
        group_offset = 0 if folder == self.builtin_plugin else 1
        plugins_set: set[str] = set(
            plugins.split(",") if isinstance(plugins, str) else plugins or []
        ) or set(self.get_plugins(folder=folder))

        for path in self.modules_list(folder=folder):
            if path.stem not in plugins_set:
                continue

            module_path = ".".join(path.with_suffix("").parts)
            module = importlib.import_module(module_path)
            # TODO: reload the module after import

            for _, obj in inspect.getmembers(module):
                handlers = getattr(obj, "handlers", None)
                if not isinstance(handlers, list):
                    continue

                for handler, group in handlers:
                    if isinstance(handler, Handler) and isinstance(group, int):
                        group = (
                            0
                            if (group < 0 and group_offset != 0)
                            else (group + group_offset)
                        )
                        yield (handler, group)

    def handler_is_loaded(self, handler: Handler, group: int = 0) -> bool:
        result = self.dispatcher.groups.get(group)
        return result is not None and handler in result

    def set_plugins_status(
        self, plugins: list[str] | set[str] | str | None, enabled: bool = True
    ):
        if not plugins:
            return

        plugins_set: set[str] = set(
            plugins.split(",") if isinstance(plugins, str) else plugins
        )

        with Session(Settings.engine) as session:
            for plugin in plugins_set:
                session.merge(PluginDatabase(name=plugin, enabled=enabled))

            session.commit()

    def get_plugin_status(self, plugin: str) -> bool:
        with Session(Settings.engine) as session:
            enabled = session.execute(
                select(PluginDatabase.enabled).where(
                    PluginDatabase.name.is_(plugin)
                )
            ).scalar()
            return bool(enabled)

    def load_plugins(self) -> None:
        self.custom_load_plugins()

    def custom_load_plugins(
        self,
        plugins: str | list[str] | None = None,
        folder: str | list[str] | None = None,
        force_load: bool = False,
    ) -> dict[str, str]:
        result = {}
        plugins_set: set[str] = set(
            plugins.split(",") if isinstance(plugins, str) else plugins or []
        )
        all_plugins = set(self.get_plugins(folder=folder))
        plugins_set = plugins_set or all_plugins
        valid_plugins = plugins_set.intersection(all_plugins)
        disabled_plugins = set()

        if not force_load:
            with Session(Settings.engine) as session:
                stmt = select(PluginDatabase.name).where(
                    PluginDatabase.name.in_(plugins_set),
                    PluginDatabase.enabled.is_(False),
                )
                disabled_plugins = set(session.execute(stmt).scalars().all())

        plugins_set.difference_update(
            disabled_plugins.intersection(valid_plugins)
        )
        self.set_plugins_status(plugins, True)

        for handler in self.get_handlers(plugins, folder=folder):
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
        plugins: str | list[str] | None = None,
        folder: str | list[str] | None = None,
    ):
        result = {}
        plugins_set: set[str] = set(
            plugins.split(",") if isinstance(plugins, str) else plugins or []
        ).intersection(self.get_plugins(folder=folder))

        self.set_plugins_status(plugins_set, False)

        for handler in self.get_handlers(plugins_set, folder=folder):
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
