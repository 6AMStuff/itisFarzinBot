import inspect
import logging
import logging.handlers
import os
import re
import time
from typing import ClassVar, cast
from zoneinfo import ZoneInfo

import sqlalchemy
import yaml
from pyrogram import filters
from sqlalchemy import JSON, Boolean, String
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Config:
    config: dict[str, object]
    config_path = "config/config.yaml"
    default_values: ClassVar[dict[str, object]] = {
        "client_name": "itisFarzin",
        "api_id": None,
        "api_hash": None,
        "bot_token": None,
        "in_memory": False,
        "plugins_folder": "plugins",
        "log_level": 20,
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

    def __init__(self) -> None:
        self.config = {}

        if os.path.exists(self.config_path):
            with open(self.config_path) as file:
                self.config = yaml.safe_load(file)

    def __getitem__(self, key: str) -> "Value | None":
        value = next(
            (
                value
                for value in (
                    os.getenv(key.upper()),
                    self.config.get(key.lower()),
                    self.default_values.get(key),
                )
                if value is not None
            ),
            None,
        )
        return Value(value) if value is not None else None

    get = __getitem__


config = Config()


class Value(str):
    def __new__(cls, value: object = None) -> "Value":
        s = "" if value is None else str(value)
        return cast("Value", super().__new__(cls, s))

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

    def as_optional(self) -> str | None:
        return str(self) if len(self) > 0 else None


class Settings:
    @staticmethod
    def url_parser(url: str | None) -> dict[str, int | str] | None:
        if url is None:
            return None

        pattern = re.compile(
            r"^(?:(?P<scheme>[a-zA-Z0-9]+)://)?"  # Optional scheme
            r"(?:(?P<username>[^:]+)"  # Optional username
            r"(?::(?P<password>[^@]+))?@)?"  # Optional password
            r"(?P<hostname>[^:]+)"  # Hostname
            r":(?P<port>\d+)$"  # Port
        )

        result = pattern.match(url)
        if result is None:
            return None

        return {
            key: int(value) if str(value).isdigit() else str(value)
            for key, value in result.groupdict().items()
        }

    @staticmethod
    def getenv(key: str, default: object = None) -> Value:
        value = config.get(key.lower())
        return Value(value if value is not None else default)

    @staticmethod
    def infer_plugin_name() -> str | None:
        frame = inspect.currentframe()
        try:
            if (
                frame is None
                or frame.f_back is None
                or frame.f_back.f_back is None
            ):
                return None

            module = frame.f_back.f_back.f_globals.get("__name__")
            if not isinstance(module, str):
                return None

            return module.rsplit(".", 1)[-1]
        finally:
            del frame

    @staticmethod
    def _createdata(plugin_name: str) -> None:
        with Session(Settings.engine) as session:
            _ = session.merge(PluginDatabase(name=plugin_name, enabled=True))
            session.commit()

    @staticmethod
    def setdata(
        key: str, value: object, plugin_name: str | None = None
    ) -> bool:
        if plugin_name is None:
            inferred = Settings.infer_plugin_name()
            if inferred is None:
                return False

            plugin_name = inferred

        with Session(Settings.engine) as session:
            data: dict[str, object] | None = session.execute(
                sqlalchemy.select(PluginDatabase.custom_data).where(
                    PluginDatabase.name == plugin_name
                )
            ).scalar()
            if data is None:
                Settings._createdata(plugin_name)
                data = {}

            data[key] = value
            result = session.execute(
                sqlalchemy.update(PluginDatabase)
                .where(PluginDatabase.name == plugin_name)
                .values(custom_data=data)
            )
            session.commit()

            if isinstance(result, sqlalchemy.engine.cursor.CursorResult):
                return result.rowcount > 0

            return False

    @staticmethod
    def getdata(
        key: str,
        default: str | int | bool | None = None,
        use_env: bool = False,
        plugin_name: str | None = None,
    ) -> Value:
        if plugin_name is None:
            inferred = Settings.infer_plugin_name()
            if inferred is None:
                return Value()

            plugin_name = inferred

        with Session(Settings.engine) as session:
            data: dict[str, object] | None = session.execute(
                sqlalchemy.select(PluginDatabase.custom_data).where(
                    PluginDatabase.name == plugin_name
                )
            ).scalar()
            if data is None:
                Settings._createdata(plugin_name)
                data = {}

            value = data.get(
                key,
                Settings.getenv(key, default) if use_env else default,
            )
            return Value(value)

    @staticmethod
    def deldata(key: str, plugin_name: str | None = None) -> bool:
        if plugin_name is None:
            inferred = Settings.infer_plugin_name()
            if inferred is None:
                return False

            plugin_name = inferred

        with Session(Settings.engine) as session:
            data = session.execute(
                sqlalchemy.select(PluginDatabase.custom_data).where(
                    PluginDatabase.name == plugin_name
                )
            ).scalar()
            if data is None:
                Settings._createdata(plugin_name)
                return True

            if key in data:
                del data[key]
            else:
                return False

            result = session.execute(
                sqlalchemy.update(PluginDatabase)
                .where(PluginDatabase.name == plugin_name)
                .values(custom_data=data)
            )
            session.commit()

            if isinstance(result, sqlalchemy.engine.cursor.CursorResult):
                return result.rowcount > 0

            return False

    @staticmethod
    def apply_timezone() -> Value:
        tz = config.get("tz")

        if not isinstance(tz, Value) or tz.as_optional() is None:
            tz = Value("Europe/London")

        try:
            _ = ZoneInfo(tz)
        except Exception:
            tz = Value("Europe/London")

        os.environ["TZ"] = tz
        time.tzset()

        return tz

    engine = sqlalchemy.create_engine(getenv("db_uri"), pool_pre_ping=True)

    PROXY = getenv(
        "proxy",
        (
            (
                getenv("http_proxy")
                if len(getenv("http_proxy")) > 0
                else getenv("https_proxy")
            )
            if getenv("use_system_proxy").is_enabled
            else None
        ),
    ).as_optional()
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
    custom_data: Mapped[dict[str, object]] = mapped_column(
        JSON(), default=dict()
    )


logger = logging.getLogger("bot")
log_level = (
    Settings.getenv("log_level").to_int
    if Settings.getenv("log_level").is_digit
    else logging.INFO
)

in_memory = Settings.getenv("in_memory").is_enabled

if in_memory:
    log_handler = logging.StreamHandler()
else:
    log_handler = logging.handlers.RotatingFileHandler(
        filename="config/bot.log",
        maxBytes=Settings.getenv("log_max_size_mb").to_int * 1024 * 1024,
        backupCount=Settings.getenv("log_backup_count").to_int,
    )

log_handler.setLevel(log_level)
formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
log_handler.setFormatter(formatter)
logging.basicConfig(
    level=log_handler.level,
    format=formatter._style._fmt,
    datefmt=formatter.datefmt,
    handlers=[log_handler],
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
