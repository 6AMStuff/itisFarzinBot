import os
from pyrogram import Client

from config import (API_HASH, API_ID, BOT_TOKEN, PLUGIN_FOLDER, PROXY,
                    url_parser)


app = Client("data/" + os.getenv("client_name", "itisFarzin"),
             api_id=API_ID,
             api_hash=API_HASH,
             bot_token=BOT_TOKEN,
             proxy=url_parser(PROXY, proxy_mode=True),
             plugins=dict(root=PLUGIN_FOLDER))


if __name__ == "__main__":
    app.run()
