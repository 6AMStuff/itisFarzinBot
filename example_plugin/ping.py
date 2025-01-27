from pyrogram import Client, filters
from pyrogram.types import Message

from config import IS_ADMIN, CMD_PREFIXES


@Client.on_message(IS_ADMIN & filters.command("ping", CMD_PREFIXES))
async def pong(_, message: Message):
    await message.reply("Pong!")
