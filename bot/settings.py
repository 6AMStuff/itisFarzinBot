import os
import re
import time
import yaml
import inspect
import logging
from typing import Any
import logging.handlers
from pathlib import Path
from pyrogram import filters
from zoneinfo import ZoneInfo
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
    "admins": "@FarzinKazemzadeh @itisFarzin",
    "tz": "Europe/London",
    "proxy": None,
    "use_system_proxy": True,
    "cmd_prefixes": ". /",
    "db_uri": "sqlite:///config/database.db",
    "plugins_repo": "https://github.com/6AMStuff/itisFarzinBotPlugins",
}

config.update(yaml.safe_load(Path("config/config.yaml").read_text()))


class Value(str):
    def __new__(cls, value: str | int | bool | None = None):
        s = str(value or "")
        return str.__new__(cls, s)

    @property
    def is_enabled(self) -> bool:
        return self.lower() in {"true", "1"}

    @property
    def is_digit(self) -> bool:
        return self.isdigit()

    @property
    def to_int(self) -> int:
        return int(self)

    @property
    def to_float(self) -> float:
        return float(self)

    @property
    def to_str(self) -> str:
        return str(self)


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
    def infer_plugin_name() -> str | None:
        frame = inspect.currentframe()
        try:
            if not frame or not frame.f_back or not frame.f_back.f_back:
                return None

            module = frame.f_back.f_back.f_globals.get("__name__")
            if not isinstance(module, str):
                return None

            return module.rsplit(".", 1)[-1]
        finally:
            del frame

    @staticmethod
    def _createdata(plugin_name: str):
        with Session(Settings.engine) as session:
            session.merge(PluginDatabase(name=plugin_name, enabled=True))
            session.commit()

    @staticmethod
    def setdata(key: str, value: Any, plugin_name: str | None = None) -> bool:
        plugin_name = plugin_name or Settings.infer_plugin_name()
        if not plugin_name:
            return False

        with Session(Settings.engine) as session:
            data = session.execute(
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
        default: Any = None,
        use_env: bool = False,
        plugin_name: str | None = None,
    ):
        plugin_name = plugin_name or Settings.infer_plugin_name()
        if not plugin_name:
            return Value()

        with Session(Settings.engine) as session:
            data = session.execute(
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
                    Settings.getenv(key, default) if use_env else default,
                )
            )

    @staticmethod
    def deldata(key: str, plugin_name: str | None = None) -> bool:
        plugin_name = plugin_name or Settings.infer_plugin_name()
        if not plugin_name:
            return False

        with Session(Settings.engine) as session:
            data = session.execute(
                select(PluginDatabase.custom_data).where(
                    PluginDatabase.name == plugin_name
                )
            ).scalar()
            if not data:
                Settings._createdata(plugin_name)
                return True

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
    def apply_timezone():
        tz = os.getenv("TZ") or config.get("tz")
        if tz:
            try:
                ZoneInfo(tz)
            except Exception:
                tz = None

        tz = tz or "Europe/London"

        os.environ["TZ"] = tz
        time.tzset()

        return tz

    engine = create_engine(getenv("db_uri"), pool_pre_ping=True)

    PROXY = getenv(
        "proxy",
        (
            getenv("http_proxy") or getenv("https_proxy")
            if getenv("use_system_proxy").is_enabled
            else None
        ),
    )
    ADMINS = getenv("admins").split(" ")
    IS_ADMIN = filters.user(list(ADMINS))
    CMD_PREFIXES = getenv("cmd_prefixes").split(" ")
    REGEX_CMD_PREFIXES = "|".join(map(re.escape, CMD_PREFIXES))
    TIMEZONE = ZoneInfo(apply_timezone())
    TEST_MODE = getenv("test_mode").is_enabled


class DataBase(DeclarativeBase):
    pass


class PluginDatabase(DataBase):
    __tablename__ = "plugins"

    name: Mapped[str] = mapped_column(String(40), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean())
    custom_data: Mapped[dict[str, Any]] = mapped_column(JSON(), default=dict())


logger = logging.getLogger(Settings.getenv("log_name"))
log_level = (
    Settings.getenv("log_level").to_int
    if Settings.getenv("log_level").is_digit
    else logging.INFO
)
file_handler = logging.handlers.RotatingFileHandler(
    filename=f"{Settings.getenv('log_dir')}/{logger.name}.log",
    maxBytes=Settings.getenv("log_max_size_mb").to_int * 1024 * 1024,
    backupCount=Settings.getenv("log_backup_count").to_int,
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
    format=formatter._fmt or "",
    datefmt=formatter.datefmt,
    handlers=[file_handler],
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
