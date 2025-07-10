import os
import sys
import uvloop
import asyncio
import subprocess
from bot import Bot
from pyrogram.methods.utilities.idle import idle

from config import Config

plugins_folder = Config.getenv("plugins_folder", "plugins")


async def main():
    app = Bot(
        "data/" + str(Config.getenv("client_name", "itisFarzin")),
        api_id=Config.getenv("api_id"),
        api_hash=Config.getenv("api_hash"),
        bot_token=Config.getenv("bot_token"),
        proxy=Config.url_parser(Config.PROXY, is_a_proxy=True),
        plugins=dict(root=plugins_folder),
    )
    await app.start()
    await idle()
    await app.stop()


def requirements():
    for dirpath, __, filenames in os.walk(plugins_folder, followlinks=True):
        if "requirements.txt" in filenames:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "--disable-pip-version-check",
                    "-r",
                    os.path.join(dirpath, "requirements.txt"),
                ],
            )


if __name__ == "__main__":
    if Config.getenv("test_mode") not in {"true", "1"}:
        requirements()

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())
