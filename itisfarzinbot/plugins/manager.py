from __future__ import annotations

from datetime import datetime

import humanize
from pyrogram import filters

from itisfarzinbot import Bot
from itisfarzinbot.settings import Settings
from itisfarzinbot.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)


def pretty_name(plugin: str) -> str:
    return plugin.replace("-", " ").replace("_", " ")


async def plugins_status(client: Bot, update: Message | CallbackQuery) -> None:
    plugins = client.get_plugins()
    text = "**Plugins**:"
    reply_markup = None

    if client.is_bot:
        keyboard = [
            [
                InlineKeyboardButton(
                    pretty_name(plugin), callback_data=f"plugins info {plugin}"
                ),
                InlineKeyboardButton(
                    "✅" if client.get_plugin_status(plugin) else "❌",
                    callback_data=f"plugins toggle {plugin}",
                ),
            ]
            for plugin in plugins
        ]
        reply_markup = InlineKeyboardMarkup(
            keyboard
            if len(keyboard) > 0
            else [
                [
                    InlineKeyboardButton(
                        "No plugins found.", callback_data="noop"
                    )
                ]
            ]
        )
    else:
        text += "\n" + "\n".join(
            f"{pretty_name(plugin)}: "
            f"{'✅' if client.get_plugin_status(plugin) else '❌'}"
            for plugin in plugins
        )

    if isinstance(update, Message):
        await update.reply(
            text,
            reply_markup=reply_markup,
        )
    elif isinstance(update, CallbackQuery):
        # Thanks for the great type annotations, kurigram!
        if reply_markup is not None:
            await update.edit_message_text(
                text=text,
                reply_markup=reply_markup,
            )
        else:
            await update.edit_message_text(
                text=text,
            )


async def plugin_detail(
    client: Bot, query: CallbackQuery, plugin: str
) -> None:
    info = client.collect_plugins().get(plugin)
    if info is None:
        await plugins_status(client, query)
        return

    modified = datetime.fromtimestamp(info.path.stat().st_mtime)
    mark = "✅" if info.enabled else "❌"
    text = "\n".join(
        [
            f"**{pretty_name(plugin)}** {mark}",
            "",
            f"• **Status:** {'Enabled' if info.enabled else 'Disabled'}",
            f"• **File:** `{info.path}`",
            f"• **Size:** {humanize.naturalsize(info.size)}",
            f"• **Handlers:** {len(info.handlers)}",
            f"• **Modified:** {modified:%Y-%m-%d %H:%M}",
        ]
    )

    if len(info.handlers) > 0:
        text += "\n\n**Handlers:**"
        for handler, _ in info.handlers:
            text += (
                f"\n• `{handler.callback.__name__}`: "
                f"{type(handler).__name__.removesuffix('Handler')}"
            )

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Disable" if info.enabled else "Enable",
                        callback_data=f"plugins toggle2 {plugin}",
                    ),
                    InlineKeyboardButton("« Back", callback_data="plugins"),
                ]
            ]
        ),
    )


@Bot.on_message(
    Settings.IS_ADMIN & filters.command("plugins", Settings.CMD_PREFIXES)
)
async def plugins(app: Bot, message: Message) -> None:
    await plugins_status(app, message)


@Bot.on_callback_query(
    Settings.IS_ADMIN
    & filters.regex(
        r"^plugins(?: (?P<action>info|toggle|toggle2) (?P<plugin>[\w\-]+))?$"
    )
)
async def plugins_callback(app: Bot, query: CallbackQuery) -> None:
    if not isinstance(query.matches, list) or len(query.matches) == 0:
        return

    action, plugin = query.matches[0].groups()
    if not isinstance(action, str) or not isinstance(plugin, str):
        await plugins_status(app, query)
        return

    if action in ("toggle", "toggle2"):
        if app.get_plugin_status(plugin):
            _ = app.unload_plugins(plugin)
        else:
            _ = app.custom_load_plugins(plugin, force_load=True)

    if action == "toggle":
        await plugins_status(app, query)
    else:
        await plugin_detail(app, query, plugin)


@Bot.on_message(
    Settings.IS_ADMIN & filters.command("handlers", Settings.CMD_PREFIXES)
)
async def handlers(app: Bot, message: Message) -> None:
    plugins = app.collect_plugins()

    lines = [
        f"{handler.callback.__name__} ({pretty_name(name)}): "
        + ("Loaded" if app.handler_is_loaded(handler, group) else "Not loaded")
        for name, info in plugins.items()
        for handler, group in info.handlers
    ]
    response = "**Handlers**:\n" + (
        "\n".join(lines) if len(lines) > 0 else "No handlers found."
    )
    await message.reply(response)


@Bot.on_message(
    Settings.IS_ADMIN
    & filters.command(["load", "unload"], Settings.CMD_PREFIXES)
)
async def load_unload(app: Bot, message: Message) -> None:
    if message.command is None or len(message.command) == 0:
        return

    plugins = (
        ",".join(message.command[-1:]) if len(message.command) > 1 else None
    )
    if message.command[0] == "load":
        result = app.custom_load_plugins(plugins, force_load=True)
    else:
        result = app.unload_plugins(plugins)

    response = "\n".join(
        [f"**{plugin}**: {result[plugin]}" for plugin in result]
    )
    await message.reply(response)


__all__ = ("handlers", "load_unload", "plugins", "plugins_callback")
__plugin__ = True
__bot_only__ = False
