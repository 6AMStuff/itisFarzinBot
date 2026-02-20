from bot import Bot
from pyrogram import filters
from bot.types import Message

from bot.settings import Settings


@Bot.on_message(
    Settings.IS_ADMIN & filters.command("setdata", Settings.CMD_PREFIXES)
)
async def setdata(app: Bot, message: Message) -> None:
    if not message.command:
        return

    if len(message.command) != 4:
        await message.reply(
            f"{Settings.CMD_PREFIXES[0]}setdata [plugin name] [key] [value]"
        )
        return

    _, plugin_name, key, value = message.command
    if plugin_name not in app.get_plugins():
        await message.reply(f"Plugin {plugin_name} doesn't exist.")
        return

    result = Settings.setdata(key, value, plugin_name=plugin_name)
    await app.call_data_change(plugin_name)
    await message.reply("Done." if result else "Failed.")


@Bot.on_message(
    Settings.IS_ADMIN & filters.command("getdata", Settings.CMD_PREFIXES)
)
async def getdata(app: Bot, message: Message) -> None:
    if not message.command:
        return

    if len(message.command) != 3:
        await message.reply(
            f"{Settings.CMD_PREFIXES[0]}getdata [plugin name] [key]"
        )
        return

    _, plugin_name, key = message.command
    if plugin_name not in app.get_plugins():
        await message.reply(f"Plugin {plugin_name} doesn't exist.")
        return

    result = Settings.getdata(key, plugin_name=plugin_name)
    await message.reply(f"Value: `{result}`")


@Bot.on_message(
    Settings.IS_ADMIN & filters.command("deldata", Settings.CMD_PREFIXES)
)
async def deldata(app: Bot, message: Message) -> None:
    if not message.command:
        return

    if len(message.command) != 3:
        await message.reply(
            f"{Settings.CMD_PREFIXES[0]}deldata [plugin name] [key]"
        )
        return

    _, plugin_name, key = message.command
    if plugin_name not in app.get_plugins():
        await message.reply(f"Plugin {plugin_name} doesn't exist.")
        return

    result = Settings.deldata(key, plugin_name=plugin_name)
    await app.call_data_change(plugin_name)
    await message.reply("Done." if result else "Failed.")


__all__ = ("deldata", "getdata", "setdata")
__plugin__ = True
__bot_only__ = False
