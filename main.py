import os
from bot import Bot
from setup import setup_environment

from config import Config

plugins_folder = Config.getenv("plugins_folder", "plugins")
app = Bot(
    "data/" + str(Config.getenv("client_name", "itisFarzin")),
    api_id=Config.getenv("api_id"),
    api_hash=Config.getenv("api_hash"),
    bot_token=Config.getenv("bot_token"),
    proxy=Config.url_parser(Config.PROXY, is_a_proxy=True),
    plugins=dict(root=plugins_folder)
)


if __name__ == "__main__":
    for root, _, files in os.walk(plugins_folder, followlinks=True):
        for file in files:
            if file == "requirements.txt":
                setup_environment(f"{root}/{file}", False)
    app.run()
