import time
from pyrogram.types import Message
from sqlalchemy.orm import Session
from sqlalchemy import delete, select
from pyrogram import Client, filters, errors

from config import Config, AdminDatabase


@Client.on_message(
    Config.IS_ADMIN
    & filters.command(["addadmin", "deladmin", "admins"], Config.CMD_PREFIXES)
)
async def admin(app: Client, message: Message):
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
                    delete(AdminDatabase).where(AdminDatabase.id == user.id)
                )
                session.commit()
                await message.reply("Done.")
        case "admins":
            with Session(Config.engine) as session:
                admins = session.execute(select(AdminDatabase.id)).all()
                admin_ids = [admin[0] for admin in admins]
                if len(admin_ids) == 0:
                    msg = "There are no admin."
                else:
                    msg = "List of admins:\n"
                    for i, admin_id in enumerate(admin_ids, start=1):
                        try:
                            admin = await app.get_users(admin_id)
                            if admin:
                                msg += f"{i}. {admin.mention}\n"
                                continue
                        except errors.PeerIdInvalid:
                            pass
                        msg += f"{i}. `{admin_id}`\n"
                await message.reply(msg)


__all__ = ["admin"]
__plugin__ = True
