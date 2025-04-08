from pyrogram import Client, filters
from pyrogram.types import Message

from config import Config


@Client.on_message(
    Config.IS_ADMIN & filters.command("ping", Config.CMD_PREFIXES)
)
async def pong(_, message: Message):
    await message.reply("Pong!")


__all__ = ["pong"]
__plugin__ = True
