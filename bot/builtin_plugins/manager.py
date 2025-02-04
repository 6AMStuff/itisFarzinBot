from bot import Bot
from pyrogram import filters
from pyrogram.types import Message

from config import Config


@Bot.on_message(
    Config.IS_ADMIN & filters.command("plugins", Config.CMD_PREFIXES)
)
async def plugins(app: Bot, message: Message):
    await message.reply("**Plugins**: " + ", ".join(app.plugin_list()))


@Bot.on_message(
    Config.IS_ADMIN & filters.command("handlers", Config.CMD_PREFIXES)
)
async def handlers(app: Bot, message: Message):
    responce = "**Handlers**:\n" + "\n".join([
        f"{handler.callback.__name__}: "
        + "Loaded" if app.handler_is_loaded(handler, group) else "Not loaded"
        for handler, group in app.get_handlers(app.plugin_list())
    ])
    await message.reply(responce)


@Bot.on_message(
    Config.IS_ADMIN & filters.command("load", Config.CMD_PREFIXES)
)
async def load(app: Bot, message: Message):
    plugins = (
        ",".join(message.command[-1:])
        if len(message.command) > 1 else None
    )
    result = app.load_plugins(plugins, force_load=True)
    responce = "\n".join([
        f"**{plugin}**: {result[plugin]}" for plugin in result
    ])
    await message.reply(responce)


@Bot.on_message(
    Config.IS_ADMIN & filters.command("unload", Config.CMD_PREFIXES)
)
async def unload(app: Bot, message: Message):
    plugins = (
        ",".join(message.command[-1:])
        if len(message.command) > 1 else None
    )
    result = app.unload_plugins(plugins)
    responce = "\n".join([
        f"**{plugin}**: {result[plugin]}" for plugin in result
    ])
    await message.reply(responce)
