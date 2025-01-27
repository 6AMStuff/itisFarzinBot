import os
import re
import logging
from pyrogram import filters
from dotenv import load_dotenv


load_dotenv("data/.env")

logger = logging.getLogger(os.getenv("log_name", "bot"))
log_level = os.getenv("log_level")
log_level = int(log_level) if str(log_level).isdigit() else logging.INFO
logging.basicConfig(
    filename=f"{os.getenv("log_path", ".")}/{logger.name}.log",
    level=log_level,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p"
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

API_ID = os.getenv("api_id")
API_HASH = os.getenv("api_hash")
BOT_TOKEN = os.getenv("bot_token")
PLUGIN_FOLDER = os.getenv("plugin_folder", "plugins")

IS_ADMIN = filters.user(
    os.getenv("admins", "@itisFarzin").split(",")
)
PROXY = os.getenv(
    "proxy",
    os.getenv("http_proxy") or os.getenv("HTTP_PROXY")
    if os.getenv("use_system_proxy", "yes").lower() == "yes"
    else None
)
CMD_PREFIXES = os.getenv("cmd_prefixes", "/").split(" ")


def url_parser(url: str, proxy_mode: bool = False):
    pattern = re.compile(
        r'^(?:(?P<scheme>[a-zA-Z0-9]+)://)?'  # Optional scheme
        r'(?:(?P<username>[^:]+)'  # Optional username
        r'(?::(?P<password>[^@]+))?@)?'  # Optional password
        r'(?P<hostname>[^:]+)'  # Hostname
        r':(?P<port>\d+)$'  # Port
    )
    if not url:
        return None
    result = pattern.match(str(url))

    if not result:
        return None

    if proxy_mode and (
        result["scheme"] not in ["http", "socks5", "socks4"]
    ):
        return None

    return {key: int(value) if str(value).isdigit() else value
            for key, value in result.groupdict().items()}
