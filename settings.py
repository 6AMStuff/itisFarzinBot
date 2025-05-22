import os
import re
import inspect
import logging
from pyrogram import filters
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from sqlalchemy import create_engine, String, Boolean, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


load_dotenv("data/.env")

logger = logging.getLogger(os.getenv("log_name", "bot"))
log_level = str(os.getenv("log_level"))
log_level = int(log_level) if str(log_level).isdigit() else logging.INFO
logging.basicConfig(
    filename=f'{os.getenv("log_path", "data")}/{logger.name}.log',
    level=log_level,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)


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
    def getenv(key: str, default=None):
        return os.environ.get(key, default)

    @staticmethod
    def _createdata(plugin_name: str):
        with Session(Settings.engine) as session:
            session.merge(PluginDatabase(name=plugin_name, enabled=True))
            session.commit()

    @staticmethod
    def setdata(key: str, value, plugin_name: str = None) -> bool:
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
        key: str, default=None, use_env: bool = False, plugin_name: str = None
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
            return data.get(
                key, Settings.getenv(key, default) if use_env else default
            )

    @staticmethod
    def deldata(key: str, plugin_name: str = None) -> bool:
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

    engine = create_engine(
        getenv("db_uri", "sqlite:///data/database.db"), pool_pre_ping=True
    )

    PROXY = str(
        getenv(
            "proxy",
            (
                getenv("http_proxy") or getenv("HTTP_PROXY")
                if str(getenv("use_system_proxy", "yes")).lower() == "yes"
                else None
            ),
        )
    )
    IS_ADMIN = filters.user(str(getenv("admins", "@itisFarzin")).split(","))
    CMD_PREFIXES = str(getenv("cmd_prefixes", "/")).split(" ")
    REGEX_CMD_PREFIXES = "|".join(re.escape(prefix) for prefix in CMD_PREFIXES)


class DataBase(DeclarativeBase):
    pass


class PluginDatabase(DataBase):
    __tablename__ = "plugins"

    name: Mapped[str] = mapped_column(String(40), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean())
    custom_data: Mapped[JSON] = mapped_column(JSON(), default=dict())
