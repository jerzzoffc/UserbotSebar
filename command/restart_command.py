import asyncio
import importlib

from pyrogram.types import ReplyKeyboardRemove

from clients import UserBot, bot, navy
from config import BOT_NAME, USENAME_OWNER
from database import dB
from helpers import Emoji
from plugins import _PLUGINS


async def resetuser_needed(client, message):
    query = message.data.split("_")[1]
    if query == "emoji":
        return await reset_emoji(client, message)
    elif query == "prefix":
        return await reset_prefix(client, message)
    elif query == "userbot":
        return await restart_userbot(client, message)
    elif query == "costumtext":
        return await reset_costum_text(client, message)


async def reset_costum_text(client, message):
    user_id = message.from_user.id
    proses = await message.reply("<b>Processing...</b>")
    if user_id not in navy._get_my_id:
        return await proses.edit(
            f"<b>You are not user @{bot.me.username}!!</b>",
            reply_markup=ReplyKeyboardRemove(),
        )
    try:
        await dB.set_var(user_id, "text_ping", "Ping")
        await dB.set_var(user_id, "text_uptime", "Uptime")
        owner_name = f"<a href=tg://user?id={message.from_user.id}>{message.from_user.first_name} {message.from_user.last_name or ''}</a>"
        await dB.set_var(user_id, "text_owner", f"Owner: {owner_name}")
        await dB.set_var(user_id, "text_ubot", f"{BOT_NAME}")
        await dB.set_var(user_id, "text_gcast", "Proses")
        await dB.set_var(user_id, "text_sukses", "Gcast Sukses")
        await dB.set_var(user_id, "text_help", f"🤖 {BOT_NAME} by {USENAME_OWNER}")
        await asyncio.sleep(1)
        return await proses.edit(
            "<b>Your costum text has been reset</b>", reply_markup=ReplyKeyboardRemove()
        )
    except Exception as er:
        return await proses.edit(
            f"<b>ERROR: `{str(er)}`</b>", reply_markup=ReplyKeyboardRemove()
        )


async def reset_emoji(client, message):
    user_id = message.from_user.id
    proses = await message.reply("<b>Processing...</b>")
    if user_id not in navy._get_my_id:
        return await proses.edit(
            f"<b>You are not user @{bot.me.username}!!</b>",
            reply_markup=ReplyKeyboardRemove(),
        )
    for User in navy._ubot:
        if user_id == User.me.id:
            try:
                em = Emoji(User)
                await em.reset_emoji()
                await asyncio.sleep(1)
                return await proses.edit(
                    "<b>Your costum emoji has been reset.!!</b>",
                    reply_markup=ReplyKeyboardRemove(),
                )
            except Exception as er:
                return await proses.edit(
                    f"<b>ERROR: `{str(er)}`</b>", reply_markup=ReplyKeyboardRemove()
                )


async def reset_prefix(client, message):
    mepref = [".", ",", "?", "+", "!"]
    proses = await message.reply("<b>Processing...</b>")
    user_id = message.from_user.id
    if user_id not in navy._get_my_id:
        return await proses.edit(
            f"<b>You are not user @{bot.me.username}!!</b>",
            reply_markup=ReplyKeyboardRemove(),
        )
    for x in navy._ubot:
        if x.me.id == user_id:
            x.set_prefix(x.me.id, mepref)
            await dB.set_pref(x.me.id, mepref)
            return await proses.edit(
                f"<b>Your prefix has been reset to: `{' '.join(mepref)}` .</b>",
                reply_markup=ReplyKeyboardRemove(),
            )


async def restart_userbot(client, message):
    proses = await message.reply("<b>Processing...</b>")
    user_id = message.from_user.id
    get_id = next(
        (X for X in await dB.get_userbots() if user_id == int(X["name"])), None
    )
    if get_id is None:
        return await proses.edit(
            f"<b>You are not user @{bot.me.username}!!</b>",
            reply_markup=ReplyKeyboardRemove(),
        )
    try:
        old_ubot = next((x for x in navy._ubot if x.me.id == user_id), None)
        if old_ubot:
            navy._ubot.remove(old_ubot)
            navy._get_my_id.remove(user_id)

        ubot = UserBot(**get_id)
        await ubot.start()
        for plugin in _PLUGINS:
            importlib.reload(importlib.import_module(f"plugins.{plugin}"))

        return await proses.edit(
            f"<b>✅ Userbot has been restarted {ubot.me.first_name} {ubot.me.last_name or ''} | {ubot.me.id}.</b>",
            reply_markup=ReplyKeyboardRemove(),
        )

    except Exception as error:
        return await proses.edit(f"<b>{error}</b>", reply_markup=ReplyKeyboardRemove())
