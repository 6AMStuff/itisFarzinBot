from bot import Bot
from typing import Optional
from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import Config, PluginDatabase


def plugins_keyboard(client: Bot, plugin: Optional[str] = None):

    with Session(Config.engine) as session:
        if plugin:
            enabled, public = session.execute(
                select(
                    PluginDatabase.enabled,
                    PluginDatabase.is_public_use,
                ).where(PluginDatabase.name == plugin)
            ).one()

            return [
                [
                    InlineKeyboardButton(
                        "Status", f"plugins {plugin} status2"
                    ),
                    InlineKeyboardButton(
                        {True: "✅", False: "❌"}[enabled],
                        f"plugins {plugin} status2",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Public Use", f"plugins {plugin} public"
                    ),
                    InlineKeyboardButton(
                        {True: "✅", False: "❌"}[public],
                        f"plugins {plugin} public",
                    ),
                ],
                [
                    InlineKeyboardButton("Back", "plugins"),
                ],
            ]

        keyboard = [[InlineKeyboardButton("No were plugin found.", "None")]]
        _plugins = client.get_plugins()
        plugins = session.execute(
            select(
                PluginDatabase.name,
                PluginDatabase.enabled,
                PluginDatabase.is_public_use,
            )
        ).all()
        plugins: dict[str, list[bool]] = {
            plugin[0]: plugin[1] for plugin in plugins
        }

        if len(plugins) == 0:
            return keyboard

        keyboard = [
            [
                InlineKeyboardButton(
                    plugin.replace("-", " ").replace("_", " "),
                    f"plugins {plugin}",
                ),
                InlineKeyboardButton(
                    {True: "✅", False: "❌"}[plugins[plugin]],
                    f"plugins {plugin} status1",
                ),
            ]
            for plugin in plugins
            if plugin in _plugins
        ]

    return keyboard


@Bot.on_message(
    Config.IS_ADMIN & filters.command("plugins", Config.CMD_PREFIXES)
)
async def plugins(app: Bot, message: Message):
    await message.reply(
        "**Plugins**:",
        reply_markup=InlineKeyboardMarkup(plugins_keyboard(app)),
    )


@Bot.on_callback_query(
    Config.IS_ADMIN
    & filters.regex(r"^plugins(?: (?P<plugin>[\w\-]+))?(?: (?P<mode>\w+))?$")
)
async def plugins_callback(app: Bot, query: CallbackQuery):
    plugin: str = query.matches[0].group("plugin")
    mode: str = query.matches[0].group("mode")
    text = "**Plugins**:"

    if not plugin:
        keyboard = plugins_keyboard(app)
    elif mode == "status1":
        if app.get_plugin_status(plugin):
            app.unload_plugins(plugin)
        else:
            app.load_plugins(plugin, force_load=True)
        keyboard = plugins_keyboard(app)
    else:
        text = f"Plugin **{plugin}**:"
        if mode == "status2":
            if app.get_plugin_status(plugin):
                app.unload_plugins(plugin)
            else:
                app.load_plugins(plugin, force_load=True)
        elif mode == "public":
            is_public_use = app.get_plugin_data(plugin, "is_public_use")
            app.set_plugin_data(plugin, "is_public_use", not is_public_use)
        keyboard = plugins_keyboard(app, plugin=plugin)

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )


@Bot.on_message(
    Config.IS_ADMIN & filters.command("handlers", Config.CMD_PREFIXES)
)
async def handlers(app: Bot, message: Message):
    responce = "**Handlers**:\n" + "\n".join(
        [
            f"{handler.callback.__name__}: "
            + (
                "Loaded"
                if app.handler_is_loaded(handler, group)
                else "Not loaded"
            )
            for handler, group in app.get_handlers(app.get_plugins())
        ]
    )
    await message.reply(responce)


@Bot.on_message(
    Config.IS_ADMIN & filters.command(["load", "unload"], Config.CMD_PREFIXES)
)
async def load_unload(app: Bot, message: Message):
    plugins = (
        ",".join(message.command[-1:]) if len(message.command) > 1 else None
    )
    if message.command[0] == "load":
        result = app.load_plugins(plugins, force_load=True)
    else:
        result = app.unload_plugins(plugins)
    responce = "\n".join(
        [f"**{plugin}**: {result[plugin]}" for plugin in result]
    )
    await message.reply(responce)


__all__ = ["plugins", "plugins_callback", "handlers", "load_unload"]
__plugin__ = True
