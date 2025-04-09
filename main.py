from bot import Bot

from config import Config


app = Bot(
    "data/" + str(Config.getenv("client_name", "itisFarzin")),
    api_id=Config.getenv("api_id"),
    api_hash=Config.getenv("api_hash"),
    bot_token=Config.getenv("bot_token"),
    proxy=Config.url_parser(Config.PROXY, is_a_proxy=True),
    plugins=dict(root=Config.getenv("plugin_folder", "plugins"))
)


if __name__ == "__main__":
    app.run()
