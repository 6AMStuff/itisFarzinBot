import os
import platform
import shutil
import time

import psutil
from bot import Bot
from bot.settings import Settings
from bot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram import filters, raw

pid = os.getpid()
proc = psutil.Process(pid)


def format_uptime(seconds: float) -> str:
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts: list[str] = []
    if days:
        parts.append(f"{days:.0f}d")
    if hours:
        parts.append(f"{hours:.0f}h")
    if minutes:
        parts.append(f"{minutes:.0f}m")
    if seconds or not parts:
        parts.append(f"{seconds:.0f}s")

    return " ".join(parts)


@Bot.on_message(Settings.IS_ADMIN & filters.command("status"))
async def status(app: Bot, message: Message) -> None:
    now = time.time()
    text = "**Bot Status**:\n\n"
    keyboard = None

    bot_uptime = format_uptime(now - app.uptime)
    system_uptime = format_uptime(now - psutil.boot_time())

    # ping_id value generator is from app.rnd_id()
    await app.invoke(
        raw.functions.ping.Ping(ping_id=int(now * (2**32)) & ~0b11),
    )
    ping = (time.time() - now) * 1000

    disk = shutil.disk_usage("/")
    uname = platform.uname()
    battery = psutil.sensors_battery()

    data = {
        "Bot Uptime": bot_uptime,
        "System Uptime": system_uptime,
        "Memory Usage": f"{proc.memory_info().rss / 1024**2:.2f} MB",
        "Battery Percentage": f"{battery.percent}%" if battery else None,
        "Ping": f"{ping:.3f} ms",
        "Disk Usage": (
            f"{disk.used / 1024**3:.2f} / {disk.total / 1024**3:.2f} GB"
        ),
        "Python": platform.python_version(),
        "OS": f"{uname.system} {uname.release}",
    }

    filtered_data = {k: v for k, v in data.items() if v is not None}

    if app.is_bot:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(key, callback_data="noop"),
                    InlineKeyboardButton(value, callback_data="noop"),
                ]
                for key, value in filtered_data.items()
            ]
        )
    else:
        text += "\n".join(
            [f"• **{key}:** {value}" for key, value in filtered_data.items()]
        )

    await message.reply(text, reply_markup=keyboard)


__all__ = ("status",)
__plugin__ = True
__bot_only__ = False
