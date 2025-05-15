from bot import Bot
from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from config import Config


def plugins_keyboard(app: Bot):
    plugins = app.get_plugins()
    keyboard = [
        [
            InlineKeyboardButton(
                plugin.replace("-", " ").replace("_", " "), f"plugins {plugin}"
            ),
            InlineKeyboardButton(
                {True: "✅", False: "❌"}[app.get_plugin_status(plugin)],
                f"plugins {plugin}",
            ),
        ]
        for plugin in plugins
    ]
    return keyboard or [
        [InlineKeyboardButton("No were plugin found.", "None")]
    ]


@Bot.on_message(
    Config.IS_ADMIN & filters.command("plugins", Config.CMD_PREFIXES)
)
async def plugins(app: Bot, message: Message):
    await message.reply(
        "**Plugins**:",
        reply_markup=InlineKeyboardMarkup(plugins_keyboard(app)),
    )


@Bot.on_callback_query(filters.regex(r"^plugins (?P<plugin>\w+)$"))
async def plugins_callback(app: Bot, query: CallbackQuery):
    plugin: str = query.matches[0].group("plugin")
    if app.get_plugin_status(plugin):
        app.unload_plugins(plugin)
    else:
        app.load_plugins(plugin, force_load=True)
    await query.edit_message_text(
        "**Plugins**:",
        reply_markup=InlineKeyboardMarkup(plugins_keyboard(app)),
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
