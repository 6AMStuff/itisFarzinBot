from bot import Bot
from pyrogram import filters
from bot.types import Message
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from bot.settings import Settings


async def plugins_status(client: Bot, update: Message | CallbackQuery):
    plugins = client.get_plugins()
    text = "**Plugins**:"
    reply_markup = None

    if client.is_bot:
        keyboard = [
            [
                InlineKeyboardButton(
                    plugin.replace("-", " ").replace("_", " "),
                    f"plugins {plugin}",
                ),
                InlineKeyboardButton(
                    {True: "✅", False: "❌"}[
                        client.get_plugin_status(plugin)
                    ],
                    f"plugins {plugin}",
                ),
            ]
            for plugin in plugins
        ]
        reply_markup = InlineKeyboardMarkup(
            keyboard
            or [[InlineKeyboardButton("No were plugin found.", "None")]]
        )

    else:
        text += "\n" + "\n".join(
            [
                plugin.replace("-", " ").replace("_", " ")
                + ": "
                + {True: "✅", False: "❌"}[client.get_plugin_status(plugin)]
                for plugin in plugins
            ]
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


@Bot.on_message(
    Settings.IS_ADMIN & filters.command("plugins", Settings.CMD_PREFIXES)
)
async def plugins(app: Bot, message: Message):
    await plugins_status(app, message)


@Bot.on_callback_query(
    Settings.IS_ADMIN & filters.regex(r"^plugins (?P<plugin>[\w\-]+)$")
)
async def plugins_callback(app: Bot, query: CallbackQuery):
    plugin: str = query.matches[0].group("plugin")
    if app.get_plugin_status(plugin):
        app.unload_plugins(plugin)
    else:
        app.custom_load_plugins(plugin, force_load=True)

    await plugins_status(app, query)


@Bot.on_message(
    Settings.IS_ADMIN & filters.command("handlers", Settings.CMD_PREFIXES)
)
async def handlers(app: Bot, message: Message):
    response = "**Handlers**:\n" + "\n".join(
        [
            f"{handler.callback.__name__}: "
            + (
                "Loaded"
                if app.handler_is_loaded(handler, group)
                else "Not loaded"
            )
            for handler, group in app.get_handlers(list(app.get_plugins()))
        ]
    )
    await message.reply(response)


@Bot.on_message(
    Settings.IS_ADMIN
    & filters.command(["load", "unload"], Settings.CMD_PREFIXES)
)
async def load_unload(app: Bot, message: Message):
    if not message.command:
        return

    plugins = (
        ",".join(message.command[-1:]) if len(message.command) > 1 else None
    )
    if message.command[0] == "load":
        result = app.custom_load_plugins(plugins, force_load=True)
    else:
        result = app.unload_plugins(plugins)

    responce = "\n".join(
        [f"**{plugin}**: {result[plugin]}" for plugin in result]
    )
    await message.reply(responce)


__all__ = ("handlers", "load_unload", "plugins", "plugins_callback")
__plugin__ = True
__bot_only__ = False
