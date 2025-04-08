from pyrogram import Client, filters
from pyrogram.types import Message

from config import Config


@Client.on_message(
    Config.IS_ADMIN & filters.command("setdata", Config.CMD_PREFIXES)
)
async def setdata(_, message: Message):
    if len(message.command) != 3:
        await message.reply(f"{Config.CMD_PREFIXES[0]}setdata [key] [value]")
        return
    _, key, value = message.command
    result = Config.setdata(key, value)
    await message.reply("Done." if result else "Failed.")


@Client.on_message(
    Config.IS_ADMIN & filters.command("getdata", Config.CMD_PREFIXES)
)
async def getdata(_, message: Message):
    if len(message.command) != 2:
        await message.reply(f"{Config.CMD_PREFIXES[0]}getdata [key]")
        return
    result = Config.getdata(message.command[1])
    await message.reply(result)


@Client.on_message(
    Config.IS_ADMIN & filters.command("deldata", Config.CMD_PREFIXES)
)
async def deldata(_, message: Message):
    if len(message.command) != 2:
        await message.reply(f"{Config.CMD_PREFIXES[0]}deldata [key]")
        return
    result = Config.deldata(message.command[1])
    await message.reply("Done." if result else "Failed.")


__all__ = ["setdata", "getdata", "deldata"]
__plugin__ = True
