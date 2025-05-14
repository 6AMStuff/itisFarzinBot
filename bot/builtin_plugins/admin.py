import time
from pyrogram.types import Message
from sqlalchemy.orm import Session
from pyrogram import Client, filters
from sqlalchemy import delete, select

from config import Config, AdminDatabase


@Client.on_message(
    Config.IS_ADMIN
    & filters.command(["addadmin", "deladmin"], Config.CMD_PREFIXES)
)
async def admin(_: Client, message: Message):
    action = message.command[0]

    match action:
        case "addadmin":
            if not message.reply_to_message:
                await message.reply("Reply to a user.")
                return

            if not message.reply_to_message.from_user:
                await message.reply("Can't add this user to admin list.")
                return

            user = message.reply_to_message.from_user
            with Session(Config.engine) as session:
                data = session.execute(
                    select(AdminDatabase).where(AdminDatabase.id == user.id)
                ).one_or_none()
                if data:
                    await message.reply(f"User {user.mention} is an admin.")
                    return

                session.add(
                    AdminDatabase(
                        id=user.id,
                        by_user=message.from_user.id,
                        full_name=user.full_name,
                        promote_time=time.time(),
                    )
                )
                session.commit()
                await message.reply("Done.")
        case "deladmin":
            if not message.reply_to_message:
                await message.reply("Reply to a user.")
                return

            if not message.reply_to_message.from_user:
                await message.reply("Can't remove this user from admin list.")
                return

            user = message.reply_to_message.from_user
            with Session(Config.engine) as session:
                data = session.execute(
                    select(AdminDatabase).where(AdminDatabase.id == user.id)
                ).one_or_none()
                if not data:
                    await message.reply(
                        f"User {user.mention} is not an admin."
                    )
                    return

                session.execute(
                    delete(AdminDatabase).where(
                        AdminDatabase.id == user.id
                    )
                )
                session.commit()
                await message.reply("Done.")


__all__ = ["admin"]
__plugin__ = True
