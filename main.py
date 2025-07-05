import uvloop
import asyncio
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


if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())
