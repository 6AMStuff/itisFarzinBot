import time

from pyrogram import errors, filters
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from itisfarzinbot import Bot
from itisfarzinbot.settings import AdminDatabase, Settings
from itisfarzinbot.types import Message


@Bot.on_message(
    Settings.IS_ADMIN
    & filters.command(
        ["addadmin", "deladmin", "admins"],
        Settings.CMD_PREFIXES,
    )
)
async def admin(app: Bot, message: Message) -> None:  # noqa: C901
    if message.command is None:
        return

    action = message.command[0]
    if action == "admins":
        with Session(Settings.engine) as session:
            admins = session.execute(select(AdminDatabase.id)).all()
            admin_ids = [admin_id for (admin_id,) in admins]

        if len(admin_ids) == 0:
            text = "There are no admins."
        else:
            text = "List of admins:\n"
            for i, admin_id in enumerate(admin_ids, start=1):
                try:
                    user = await app.get_users(admin_id)
                    if user is not None:
                        text += f"{i}. {user.mention}\n"
                        continue
                except errors.PeerIdInvalid:
                    pass
                text += f"{i}. `{admin_id}`\n"

        await message.reply(text)
        return

    if message.reply_to_message is None:
        await message.reply("Reply to a user.")
        return

    user = message.reply_to_message.from_user
    if user is None or message.from_user is None:
        await message.reply("Can't change this user's admin status.")
        return

    with Session(Settings.engine) as session:
        data = session.get(AdminDatabase, user.id)

        if action == "addadmin":
            if data is not None:
                await message.reply(f"User {user.mention} is an admin.")
                return

            session.add(
                AdminDatabase(
                    id=user.id,
                    by_user=message.from_user.id,
                    full_name=user.full_name,
                    promote_time=int(time.time()),
                )
            )
            session.commit()
            await message.reply("Done.")
        elif action == "deladmin":
            if data is None:
                await message.reply(f"User {user.mention} is not an admin.")
                return

            _ = session.execute(
                delete(AdminDatabase).where(AdminDatabase.id == user.id)
            )
            session.commit()
            await message.reply("Done.")


__all__ = ("admin",)
__plugin__ = True
__bot_only__ = False
