from __future__ import annotations

from datetime import datetime

import humanize
from bot import Bot
from bot.settings import Settings
from bot.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from pyrogram import filters


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
                    pretty_name(plugin), f"plugins info {plugin}"
                ),
                InlineKeyboardButton(
                    "✅" if client.get_plugin_status(plugin) else "❌",
                    f"plugins toggle {plugin}",
                ),
            ]
            for plugin in plugins
        ]
        reply_markup = InlineKeyboardMarkup(
            keyboard or [[InlineKeyboardButton("No plugins found.", "None")]]
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

    if info.handlers:
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
                        f"plugins switch {plugin}",
                    ),
                    InlineKeyboardButton("« Back", "plugins"),
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
        r"^plugins(?: (?P<action>info|toggle|switch) (?P<plugin>[\w\-]+))?$"
    )
)
async def plugins_callback(app: Bot, query: CallbackQuery) -> None:
    action, plugin = query.matches[0].groups()

    if action in ("toggle", "switch") and plugin:
        if app.get_plugin_status(plugin):
            app.unload_plugins(plugin)
        else:
            app.custom_load_plugins(plugin, force_load=True)

    if action in ("info", "switch") and plugin:
        await plugin_detail(app, query, plugin)
    else:
        await plugins_status(app, query)


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
    response = "**Handlers**:\n" + ("\n".join(lines) or "No handlers found.")
    await message.reply(response)


@Bot.on_message(
    Settings.IS_ADMIN
    & filters.command(["load", "unload"], Settings.CMD_PREFIXES)
)
async def load_unload(app: Bot, message: Message) -> None:
    if not message.command:
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
