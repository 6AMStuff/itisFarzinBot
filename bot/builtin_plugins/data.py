import os
import inspect
import importlib
from bot import Bot
from pathlib import Path
from typing import Callable
from pyrogram import filters
from pyrogram.types import Message

from config import Config


original___name__ = __name__


async def notify_module_data_change(folder: str, name: str) -> bool:
    name = name.rsplit(".py", 1)[0] + ".py"

    for root, _, files in os.walk(folder, followlinks=True):
        for file in files:
            if file == name:
                path = Path(root) / file
                module_path = ".".join(path.with_suffix("").parts)
                module = importlib.import_module(module_path)
                if on_data_change := getattr(module, "on_data_change", None):
                    if not isinstance(on_data_change, Callable):
                        pass
                    if inspect.iscoroutinefunction(on_data_change):
                        await on_data_change()
                    else:
                        on_data_change()
                    return True
                break
    return False


@Bot.on_message(
    Config.IS_ADMIN & filters.command("setdata", Config.CMD_PREFIXES)
)
async def setdata(app: Bot, message: Message):
    if len(message.command) != 4:
        await message.reply(
            f"{Config.CMD_PREFIXES[0]}setdata [plugin name] [key] [value]"
        )
        return
    _, plugin_name, key, value = message.command
    if plugin_name not in app.get_plugins():
        await message.reply(f"Plugin {plugin_name} doesn't exist.")
        return
    globals()["__name__"] = plugin_name
    result = Config.setdata(key, value)
    globals()["__name__"] = original___name__
    await notify_module_data_change(app.plugins["root"], plugin_name)
    await message.reply("Done." if result else "Failed.")


@Bot.on_message(
    Config.IS_ADMIN & filters.command("getdata", Config.CMD_PREFIXES)
)
async def getdata(app: Bot, message: Message):
    if len(message.command) != 3:
        await message.reply(
            f"{Config.CMD_PREFIXES[0]}getdata [plugin name] [key]"
        )
        return
    _, plugin_name, key = message.command
    if plugin_name not in app.get_plugins():
        await message.reply(f"Plugin {plugin_name} doesn't exist.")
        return
    globals()["__name__"] = plugin_name
    result = Config.getdata(key)
    globals()["__name__"] = original___name__
    await message.reply(f"Value: `{result}`")


@Bot.on_message(
    Config.IS_ADMIN & filters.command("deldata", Config.CMD_PREFIXES)
)
async def deldata(app: Bot, message: Message):
    if len(message.command) != 3:
        await message.reply(
            f"{Config.CMD_PREFIXES[0]}deldata [plugin name] [key]"
        )
        return
    _, plugin_name, key = message.command
    if plugin_name not in app.get_plugins():
        await message.reply(f"Plugin {plugin_name} doesn't exist.")
        return
    globals()["__name__"] = plugin_name
    result = Config.deldata(key)
    globals()["__name__"] = original___name__
    await notify_module_data_change(app.plugins["root"], plugin_name)
    await message.reply("Done." if result else "Failed.")


__all__ = ["setdata", "getdata", "deldata"]
__plugin__ = True
