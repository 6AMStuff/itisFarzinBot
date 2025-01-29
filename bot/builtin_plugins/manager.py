from bot import Bot
from pyrogram import filters
from pyrogram.types import Message

from config import IS_ADMIN, CMD_PREFIXES


@Bot.on_message(IS_ADMIN & filters.command("plugins", CMD_PREFIXES))
async def plugins(app: Bot, message: Message):
    await message.reply("**Plugins**: " + ", ".join(app.plugin_list()))


@Bot.on_message(IS_ADMIN & filters.command("handlers", CMD_PREFIXES))
async def handlers(app: Bot, message: Message):
    responce = "**Handlers**:\n" + "\n".join([
        f"{handler.callback.__name__}: "
        f"{'Loaded' if app.is_loaded(handler, group) else 'Not loaded'}"
        for handler, group in app.get_handlers(app.plugin_list())
    ])
    await message.reply(responce)


@Bot.on_message(IS_ADMIN & filters.command("load", CMD_PREFIXES))
async def load(app: Bot, message: Message):
    plugins = (",".join(message.command[-1:])
               if len(message.command) > 1 else None)
    result = app.load_plugins(plugins)
    responce = "\n".join([
        f"**{plugin}**: {result[plugin]}" for plugin in result
    ])
    await message.reply(responce)


@Bot.on_message(IS_ADMIN & filters.command("unload", CMD_PREFIXES))
async def unload(app: Bot, message: Message):
    plugins = (",".join(message.command[-1:])
               if len(message.command) > 1 else None)
    result = app.unload_plugins(plugins)
    responce = "\n".join([
        f"**{plugin}**: {result[plugin]}" for plugin in result
    ])
    await message.reply(responce)
