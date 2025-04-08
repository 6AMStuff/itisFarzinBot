from bot import Bot
from pyrogram.types import Message
from pyrogram import Client, filters

from config import Config


original___name__ = __name__


@Client.on_message(
    Config.IS_ADMIN & filters.command("setdata", Config.CMD_PREFIXES)
)
async def setdata(app: Bot, message: Message):
    if len(message.command) != 4:
        await message.reply(
            f"{Config.CMD_PREFIXES[0]}setdata [plugin name] [key] [value]"
        )
        return
    _, plugin_name, key, value = message.command
    if plugin_name not in app.plugin_list():
        await message.reply(f"Plugin {plugin_name} doesn't exist.")
        return
    globals()["__name__"] = plugin_name
    result = Config.setdata(key, value)
    globals()["__name__"] = original___name__
    await message.reply("Done." if result else "Failed.")


@Client.on_message(
    Config.IS_ADMIN & filters.command("getdata", Config.CMD_PREFIXES)
)
async def getdata(app: Bot, message: Message):
    if len(message.command) != 3:
        await message.reply(
            f"{Config.CMD_PREFIXES[0]}getdata [plugin name] [key]"
        )
        return
    _, plugin_name, key = message.command
    if plugin_name not in app.plugin_list():
        await message.reply(f"Plugin {plugin_name} doesn't exist.")
        return
    globals()["__name__"] = plugin_name
    result = Config.getdata(key)
    globals()["__name__"] = original___name__
    await message.reply(f"Value: `{result}`")


@Client.on_message(
    Config.IS_ADMIN & filters.command("deldata", Config.CMD_PREFIXES)
)
async def deldata(app: Bot, message: Message):
    if len(message.command) != 3:
        await message.reply(
            f"{Config.CMD_PREFIXES[0]}deldata [plugin name] [key]"
        )
        return
    _, plugin_name, key = message.command
    if plugin_name not in app.plugin_list():
        await message.reply(f"Plugin {plugin_name} doesn't exist.")
        return
    globals()["__name__"] = plugin_name
    result = Config.deldata(key)
    globals()["__name__"] = original___name__
    await message.reply("Done." if result else "Failed.")


__all__ = ["setdata", "getdata", "deldata"]
