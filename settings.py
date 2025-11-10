import os
import re
import time
import yaml
import inspect
import logging
import logging.handlers
from pathlib import Path
from pyrogram import filters
from zoneinfo import ZoneInfo
from typing import Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from sqlalchemy import create_engine, String, Boolean, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


config = {
    "client_name": "itisFarzin",
    "api_id": None,
    "api_hash": None,
    "bot_token": None,
    "in_memory": False,
    "plugins_folder": "plugins",
    "log_name": "bot",
    "log_level": 20,
    "log_dir": "config",
    "log_max_size_mb": 1,
    "log_backup_count": 2,
    "admins": ["@FarzinKazemzadeh", "@itisFarzin"],
    "tz": "Europe/London",
    "proxy": None,
    "use_system_proxy": True,
    "cmd_prefixes": [".", "/"],
    "db_uri": "sqlite:///config/database.db",
    "plugins_repo": "https://github.com/6AMStuff/itisFarzinBotPlugins",
}

config.update(yaml.safe_load(Path("config/config.yaml").read_text()))


class Value(str):
    def __init__(self, value: str | int | bool):
        self._value = str(value or "")

    @property
    def is_enabled(self) -> bool:
        return self._value.lower() in {"true", "1"}

    @property
    def is_digit(self) -> bool:
        return self._value.isdigit()

    @property
    def to_int(self) -> int:
        return int(self._value)

    @property
    def to_float(self) -> float:
        return float(self._value)

    @property
    def to_str(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return self._value


class Settings:
    @staticmethod
    def url_parser(url: str, is_a_proxy: bool = False):
        pattern = re.compile(
            r"^(?:(?P<scheme>[a-zA-Z0-9]+)://)?"  # Optional scheme
            r"(?:(?P<username>[^:]+)"  # Optional username
            r"(?::(?P<password>[^@]+))?@)?"  # Optional password
            r"(?P<hostname>[^:]+)"  # Hostname
            r":(?P<port>\d+)$"  # Port
        )

        if not url:
            return None

        result = pattern.match(str(url))
        if not result:
            return None

        if is_a_proxy and (
            result["scheme"] not in ["http", "socks5", "socks4"]
        ):
            return None

        return {
            key: int(value) if str(value).isdigit() else value
            for key, value in result.groupdict().items()
        }

    @staticmethod
    def getenv(key: str, default: Any = None):
        return Value(
            next(
                (
                    value
                    for value in (
                        os.getenv(key.upper()),
                        config.get(key.lower()),
                    )
                    if value is not None
                ),
                default,
            )
        )

    @staticmethod
    def _createdata(plugin_name: str):
        with Session(Settings.engine) as session:
            session.merge(PluginDatabase(name=plugin_name, enabled=True))
            session.commit()

    @staticmethod
    def setdata(key: str, value, plugin_name: Optional[str] = None) -> bool:
        if not plugin_name:
            caller_frame = inspect.currentframe().f_back
            plugin_name = caller_frame.f_globals["__name__"].split(".")[-1]

        with Session(Settings.engine) as session:
            data: dict = session.execute(
                select(PluginDatabase.custom_data).where(
                    PluginDatabase.name == plugin_name
                )
            ).scalar()
            if not data:
                Settings._createdata(plugin_name)
                data = {}

            data[key] = value
            result = session.execute(
                update(PluginDatabase)
                .where(PluginDatabase.name == plugin_name)
                .values(custom_data=data)
            )
            session.commit()
            return result.rowcount > 0

    @staticmethod
    def getdata(
        key: str,
        default=None,
        use_env: bool = False,
        plugin_name: Optional[str] = None,
    ):
        if not plugin_name:
            caller_frame = inspect.currentframe().f_back
            plugin_name = caller_frame.f_globals["__name__"].split(".")[-1]

        with Session(Settings.engine) as session:
            data: dict = session.execute(
                select(PluginDatabase.custom_data).where(
                    PluginDatabase.name == plugin_name
                )
            ).scalar()
            if not data:
                Settings._createdata(plugin_name)
                data = {}

            return Value(
                data.get(
                    key,
                    (
                        Settings.getenv(key, default).to_str
                        if use_env
                        else default
                    ),
                )
            )

    @staticmethod
    def deldata(key: str, plugin_name: Optional[str] = None) -> bool:
        if not plugin_name:
            caller_frame = inspect.currentframe().f_back
            plugin_name = caller_frame.f_globals["__name__"].split(".")[-1]

        with Session(Settings.engine) as session:
            data: dict = session.execute(
                select(PluginDatabase.custom_data).where(
                    PluginDatabase.name == plugin_name
                )
            ).scalar()
            if not data:
                Settings._createdata(plugin_name)
                return 1

            if key in data:
                del data[key]
            else:
                return False

            result = session.execute(
                update(PluginDatabase)
                .where(PluginDatabase.name == plugin_name)
                .values(custom_data=data)
            )
            session.commit()
            return result.rowcount > 0

    @staticmethod
    def _tz():
        tz = os.getenv("TZ") or config.get("tz") or "Europe/London"
        try:
            ZoneInfo(tz)
        except Exception:
            tz = "Europe/London"

        os.environ["TZ"] = tz
        time.tzset()
        return tz

    engine = create_engine(
        getenv("db_uri", "sqlite:///config/database.db"), pool_pre_ping=True
    )

    PROXY = getenv(
        "proxy",
        (
            getenv("http_proxy") or getenv("https_proxy")
            if getenv("use_system_proxy").is_enabled
            else None
        ),
    )
    IS_ADMIN = filters.user(getenv("admins", "@itisFarzin").split(" "))
    CMD_PREFIXES = getenv("cmd_prefixes", "/").split(" ")
    REGEX_CMD_PREFIXES = "|".join(re.escape(prefix) for prefix in CMD_PREFIXES)
    TIMEZONE = ZoneInfo(_tz())
    TEST_MODE = getenv("test_mode").is_enabled


class DataBase(DeclarativeBase):
    pass


class PluginDatabase(DataBase):
    __tablename__ = "plugins"

    name: Mapped[str] = mapped_column(String(40), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean())
    custom_data: Mapped[JSON] = mapped_column(JSON(), default=dict())


logger = logging.getLogger(Settings.getenv("log_name", "bot"))
log_level = (
    Settings.getenv("log_level").to_int
    if Settings.getenv("log_level").is_digit
    else logging.INFO
)
file_handler = logging.handlers.RotatingFileHandler(
    filename=f"{Settings.getenv("log_dir", "config")}/{logger.name}.log",
    maxBytes=Settings.getenv("log_max_size_mb", 1).to_float * 1024 * 1024,
    backupCount=Settings.getenv("log_backup_count", 2).to_int,
)
file_handler.setLevel(
    Settings.getenv("log_level").to_int
    if Settings.getenv("log_level").is_digit
    else logging.INFO
)
formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
file_handler.setFormatter(formatter)
logging.basicConfig(
    level=file_handler.level,
    format=formatter._fmt,
    datefmt=formatter.datefmt,
    handlers=[file_handler],
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
