import asyncio
import os
import random
import traceback
from datetime import datetime
from gc import get_objects
from time import time
from uuid import uuid4

import requests
from pyrogram import enums, raw
from pyrogram.errors import UserNotParticipant
from pyrogram.helpers import ikb
from pyrogram.raw.functions import Ping
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.users import GetFullUser
from pyrogram.types import (Chat, InlineKeyboardButton, InlineKeyboardMarkup,
                            InlineQueryResultAnimation,
                            InlineQueryResultArticle,
                            InlineQueryResultCachedAnimation,
                            InlineQueryResultCachedDocument,
                            InlineQueryResultCachedPhoto,
                            InlineQueryResultCachedSticker,
                            InlineQueryResultCachedVideo,
                            InlineQueryResultCachedVoice,
                            InlineQueryResultPhoto, InlineQueryResultVideo,
                            InputTextMessageContent, User)

from clients import bot, navy
from config import (API_MAELYN, BOT_NAME, HELPABLE, SUDO_OWNERS, URL_LOGO,
                    USENAME_OWNER)
from database import dB, state
from helpers import (ButtonUtils, Emoji, Tools, get_time, paginate_modules,
                     query_fonts, start_time)
from helpers.card import generate_profile_card
from logs import logger

from .pmpermit_command import DEFAULT_TEXT, LIMIT

MAX_CAPTION_LENGTH = 400


async def apkan1_cmd(client, message):
    text = client.get_text(message)
    if not text:
        return await message.reply(
            f"**Please give word for search from https://an1.com/.\nExample: `{message.text.split()[0]} pou`**",
            disable_web_page_preview=True,
        )
    payload = {"search": text}
    url = "https://api.siputzx.my.id/api/apk/an1"
    response = await Tools.fetch.post(url, json=payload)
    if response.status_code != 200:
        return await message.reply(f"**Please try again later!!")
    data = response.json()["data"]
    if len(data) == 0:
        return await message.reply("<b>No apk found!!</b>")
    uniq = f"{str(uuid4())}"
    state.set(uniq.split("-")[0], uniq.split("-")[0], data)
    try:
        inline = await ButtonUtils.send_inline_bot_result(
            message,
            message.chat.id,
            bot.me.username,
            f"inline_apkan1 {uniq.split('-')[0]}",
        )
        if inline:
            return await message.delete()
    except Exception as er:
        return await message.reply(f"**ERROR**: {str(er)}")


async def apkmoddy_cmd(client, message):
    text = client.get_text(message)
    if not text:
        return await message.reply(
            f"**Please give word for search.\nExample: `{message.text.split()[0]} pou`**",
            disable_web_page_preview=True,
        )
    payload = {"search": text}
    url = "https://api.siputzx.my.id/api/apk/apkmody"
    response = await Tools.fetch.post(url, json=payload)
    if response.status_code != 200:
        return await message.reply(f"**Please try again later!!")
    data = response.json()["data"]
    if len(data) == 0:
        return await message.reply("<b>No apk found!!</b>")
    uniq = f"{str(uuid4())}"
    state.set(uniq.split("-")[0], uniq.split("-")[0], data)
    try:
        inline = await ButtonUtils.send_inline_bot_result(
            message,
            message.chat.id,
            bot.me.username,
            f"inline_apkmoddy {uniq.split('-')[0]}",
        )
        if inline:
            return await message.delete()
    except Exception as er:
        return await message.reply(f"**ERROR**: {str(er)}")


async def detcnn_cmd(_, message):
    url = f"https://api.siputzx.my.id/api/berita/cnn"
    response = await Tools.fetch.post(url)
    if response.status_code == 200:
        data = response.json()["data"]
        uniq = f"{str(uuid4())}"
        state.set(uniq.split("-")[0], "news", data)
        try:
            inline = await ButtonUtils.send_inline_bot_result(
                message,
                message.chat.id,
                bot.me.username,
                f"inline_news {uniq.split('-')[0]}",
            )
            if inline:
                return await message.delete()
        except Exception as er:
            return await message.reply(f"**ERROR**: {str(er)}")
    else:
        return await message.reply(f"**Error with status `{response.status_code}`**")


async def infoinline_cmd(_, message):
    try:
        uniq = f"{str(uuid4())}"
        await ButtonUtils.send_inline_bot_result(
            message,
            message.chat.id,
            bot.me.username,
            f"inline_info {uniq.split('-')[0]} {id(message)}",
        )
    except Exception:
        return await message.reply_text(f"<b>ERROR!! {traceback.format_exc()}.</b>")


async def help_cmd(client, message):
    em = Emoji(client)
    await em.get()
    plan = await dB.get_var(client.me.id, "plan")
    if plan == "is_pro":
        visible_helpable = HELPABLE
    elif plan == "basic":
        visible_helpable = {
            name: data for name, data in HELPABLE.items() if not data["is_pro"]
        }
    elif plan == "lite":
        visible_helpable = {
            name: data
            for name, data in HELPABLE.items()
            if not data["is_pro"] and not data["is_basic"]
        }
    if not client.get_arg(message):
        query = "help"
        chat_id = (
            message.chat.id if len(message.command) < 2 else message.text.split()[1]
        )
        try:
            inline = await ButtonUtils.send_inline_bot_result(
                message,
                chat_id,
                bot.me.username,
                query,
            )
            if inline:
                return await message.delete()
        except Exception as error:
            return await message.reply(f"{em.gagal}Error: {str(error)}")
    else:
        nama = f"{client.get_arg(message)}"
        if nama == "format":
            return await message.reply(
                f"{em.sukses}**Please see Format on inline help**"
            )
        pref = client.get_prefix(client.me.id)
        x = next(iter(pref))
        text_help2 = f"<blockquote>**🤖 {BOT_NAME} by {USENAME_OWNER}**</blockquote>"
        if nama in visible_helpable:
            return await message.reply(
                f"{visible_helpable[nama]['module'].__HELP__.format(x, text_help2)}",
            )
        else:
            return await message.reply(
                f"{em.gagal}<b>Tidak ada modul bernama <code>{nama}</code></b>"
            )


async def game_cmd(client, message):
    try:
        x = await client.get_inline_bot_results("gamee")
        msg = message.reply_to_message or message
        random_index = random.randint(0, len(x.results) - 1)
        return await client.send_inline_bot_result(
            message.chat.id,
            x.query_id,
            x.results[random_index].id,
            reply_to_message_id=msg.id,
        )
    except Exception as error:
        return await message.reply(error)


async def catur_cmd(client, message):
    em = Emoji(client)
    await em.get()
    try:
        x = await client.get_inline_bot_results("GameFactoryBot")
        msg = message.reply_to_message or message
        return await client.send_inline_bot_result(
            message.chat.id,
            x.query_id,
            x.results[0].id,
            reply_to_message_id=msg.id,
        )
    except Exception as error:
        return await message.reply(f"{em.gagal}Error: {str(error)}")


async def font_cmd(client, message):
    emo = Emoji(client)
    await emo.get()
    pref = client.get_prefix(client.me.id)
    x = next(iter(pref))
    text = client.get_text(message)
    if not text:
        return await message.reply(
            f"{emo.gagal}<b>Please give text or reply to text:\n\nExample: <code>{x}font</code> [text or reply to text]</b>"
        )
    proses_ = await emo.get_costum_text()
    pros = await message.reply(f"{emo.proses}<b>{proses_[4]}</b>")
    uniq = f"{str(uuid4())}"
    state.set(uniq.split("-")[0], "FONT", text)
    query = f"inline_font {uniq.split('-')[0]}"
    try:
        inline = await ButtonUtils.send_inline_bot_result(
            message, message.chat.id, bot.me.username, query
        )
        if inline:
            await pros.delete()
            return await message.delete()
    except Exception as error:
        return await pros.edit(f"{emo.gagal}<b>Error:</b>\n<code>{str(error)}</code>")


async def donghua_cmd(_, message):
    try:
        url = f"https://api.maelyn.sbs/api/donghuafilm/lastupdate?apikey={API_MAELYN}"
        response = await Tools.fetch.get(url)
        if response.status_code == 200:
            data = response.json()["result"]
            uniq = f"{str(uuid4())}"
            state.set(uniq.split("-")[0], "donghua", data)
            try:
                inline = await ButtonUtils.send_inline_bot_result(
                    message,
                    message.chat.id,
                    bot.me.username,
                    f"inline_donghua {uniq.split('-')[0]}",
                )
                if inline:
                    return await message.delete()
            except Exception as er:
                return await message.reply(f"**ERROR**: {str(er)}")
        else:
            return await message.reply(
                f"**Error with status `{response.status_code}`**"
            )
    except Exception as er:
        return await message.reply(f"**ERROR**: {str(er)}")


async def comic_cmd(_, message):
    try:
        url = f"https://api.maelyn.sbs/api/komiku/lastupdate?apikey={API_MAELYN}"
        response = await Tools.fetch.get(url)
        if response.status_code == 200:
            data = response.json()["result"]
            uniq = f"{str(uuid4())}"
            state.set(uniq.split("-")[0], "comic", data)
            try:
                inline = await ButtonUtils.send_inline_bot_result(
                    message,
                    message.chat.id,
                    bot.me.username,
                    f"inline_comic {uniq.split('-')[0]}",
                )
                if inline:
                    return await message.delete()
            except Exception as er:
                return await message.reply(f"**ERROR**: {str(er)}")
        else:
            return await message.reply(
                f"**Error with status `{response.status_code}`**"
            )
    except Exception as er:
        return await message.reply(f"**ERROR**: {str(er)}")


async def cardinfo_cmd(_, message):
    uniq = f"{str(uuid4())}"
    result = await ButtonUtils.send_inline_bot_result(
        message,
        message.chat.id,
        bot.me.username,
        f"inline_card_info {uniq.split('-')[0]} {id(message)}",
    )
    if result:
        return await message.delete()
    else:
        return await message.reply_text(f"**Failed to send inline result.**")


async def inline_cmd(_, message):
    uniq = f"{str(uuid4())}"
    query = f"alive {uniq.split('-')[0]}"
    try:
        inline = await ButtonUtils.send_inline_bot_result(
            message, message.chat.id, bot.me.username, query
        )
        if inline:
            return await message.delete()
    except Exception as error:
        return await message.reply(f"Error: {str(error)}")


async def ask_cmd(client, message):
    arg = client.get_text(message)
    if not arg:
        return await message.reply(
            f"<b>Please give question!!\nExample: `{message.text.split()[0]} Siapa kamu?`</b>"
        )
    uniq = f"{str(uuid4())}"
    data = {"prompt": arg, "idm": id(message)}
    state.set(uniq.split("-")[0], "chatai", data)
    proses = await message.reply("<b>Please wait a minute...</b>")
    try:
        inline = await ButtonUtils.send_inline_bot_result(
            message,
            message.chat.id,
            bot.me.username,
            f"inline_chatai {uniq.split('-')[0]}",
        )
        if inline:
            return await proses.delete()
    except Exception as er:
        return await proses.edit(f"**ERROR**: {str(er)}")


async def cat_cmd(_, message):
    try:
        uniq = f"{str(uuid4())}"
        inline = await ButtonUtils.send_inline_bot_result(
            message,
            message.chat.id,
            bot.me.username,
            f"inline_cat {uniq.split('-')[0]}",
        )
        if inline:
            return await message.delete()
    except Exception as er:
        return await message.reply(f"**ERROR**: {str(er)}")


async def bola_cmd(_, message):
    try:
        uniq = f"{str(uuid4())}"
        inline = await ButtonUtils.send_inline_bot_result(
            message,
            message.chat.id,
            bot.me.username,
            f"inline_bola {uniq.split('-')[0]}",
        )
        if inline:
            return await message.delete()
    except Exception as er:
        return await message.reply(f"**ERROR**: {str(er)}")


async def inline_card_info(results, inline):
    try:
        uniq = inline.query.split()[1]
        _id = inline.query.split()[2]
        message = next((obj for obj in get_objects() if id(obj) == int(_id)), None)
        if message:
            buttons = []

            def add_button(name, value):
                if value:
                    buttons.append(InlineKeyboardButton(name, copy_text=str(value)))

            client = message._client
            chat = message.chat
            your_id = message.from_user or message.sender_chat
            message_id = message.id
            reply = message.reply_to_message
            replied_user_id = None
            mentioned = None
            photo_id = video_id = sticker_id = animation_id = document_id = emoji_id = (
                None
            )
            if reply:
                replied_user_id = (
                    reply.from_user.id
                    if reply.from_user
                    else reply.sender_chat.id if reply.sender_chat else None
                )
                if reply.entities:
                    for entity in reply.entities:
                        if entity.custom_emoji_id:
                            emoji_id = entity.custom_emoji_id
                if reply.photo:
                    photo_id = reply.photo.file_id
                elif reply.video:
                    video_id = reply.video.file_id
                elif reply.sticker:
                    sticker_id = reply.sticker.file_id
                elif reply.animation:
                    animation_id = reply.animation.file_id
                elif reply.document:
                    document_id = reply.document.file_id

            if len(message.command) == 2:
                try:
                    split = message.text.split(None, 1)[1].strip()
                    entity = await client.get_chat(split)

                    if entity.type in [
                        enums.ChatType.GROUP,
                        enums.ChatType.SUPERGROUP,
                        enums.ChatType.CHANNEL,
                    ]:
                        mentioned = entity.id

                    else:
                        mentioned = entity.id
                except Exception:
                    return await message.reply_text(f"**User not found.**")
            add_button("Message ID", message_id)
            add_button("Your ID", your_id.id)
            add_button("Chat ID", chat.id)
            add_button("Reply Message ID", reply.id if reply else None)
            add_button("Reply User ID", replied_user_id)
            add_button("Mentioned ID", mentioned)
            add_button("Emoji ID", emoji_id)
            add_button("Photo File ID", photo_id)
            add_button("Video File ID", video_id)
            add_button("Sticker File ID", sticker_id)
            add_button("GIF File ID", animation_id)
            add_button("Document File ID", document_id)
            buttons.append(
                InlineKeyboardButton(
                    text="Close", callback_data=f"close inline_card_info {uniq} {_id}"
                )
            )
            keyboard = InlineKeyboardMarkup(
                [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
            )

            user_to_fetch = replied_user_id or mentioned or your_id.id
            profile_card_path = None

            if user_to_fetch:
                try:
                    target = await client.get_chat(user_to_fetch)
                    if target.type == enums.ChatType.PRIVATE:
                        user = await client.get_users(user_to_fetch)
                        profile_card_path = await generate_profile_card(client, user)
                    elif target.type in [
                        enums.ChatType.GROUP,
                        enums.ChatType.SUPERGROUP,
                        enums.ChatType.CHANNEL,
                    ]:
                        user = await client.get_chat(user_to_fetch)
                        profile_card_path = await generate_profile_card(client, user)
                except Exception:
                    logger.error(f"Error: {traceback.format_exc()}")
                    profile_card_path = None
            text = f"<b><blockquote>Generated Card Info By {bot.me.mention}</blockquote></b>"
            if profile_card_path and os.path.exists(profile_card_path):
                try:
                    uploaded_url = await Tools.upload_thumb(profile_card_path)
                except Exception:
                    uploaded_url = None
                os.remove(profile_card_path)
                if uploaded_url is not None:
                    results.append(
                        InlineQueryResultPhoto(
                            photo_url=uploaded_url,
                            title="User ID Info",
                            caption=text,
                            reply_markup=keyboard,
                        )
                    )
                else:
                    results.append(
                        InlineQueryResultArticle(
                            title="User ID Info",
                            input_message_content=InputTextMessageContent(text),
                            reply_markup=keyboard,
                        )
                    )
            else:
                results.append(
                    InlineQueryResultArticle(
                        title="User ID Info",
                        input_message_content=InputTextMessageContent(text),
                        reply_markup=keyboard,
                    )
                )

            return results

    except Exception:
        logger.error(f"Inline ID Info Error:\n{traceback.format_exc()}")
        return results


async def inline_autobc(results, inline):
    chat = int(inline.query.split()[1])
    _id = inline.query.split()[2]
    try:
        message = next((obj for obj in get_objects() if id(obj) == int(_id)), None)
        if not message:
            return results
        client = message._client
        per_page = 50
        page = 0
        keyboard = []
        row = []
        title, data = await client.parse_topic(chat)
        print(f"Title: {title}")
        print(f"Data: {data}")
        try:
            sliced = data[page * per_page : (page + 1) * per_page]
            caption = f"<blockquote expandable><b>List Topic {title}\nSilahkan pilih topic untuk diatur:\n</b>"
            for idx, topic in enumerate(sliced):
                caption += f"<b>{idx + 1}. {topic['title']}</b>\n"
                button = InlineKeyboardButton(
                    text=str(idx + 1),
                    callback_data=f"selectedtopic_{chat}_{topic['id']}_{topic['title']}",
                )
                row.append(button)
                if (idx + 1) % 5 == 0:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
            reply_markup = InlineKeyboardMarkup(keyboard)
            caption += "</blockquote>"
        except Exception:
            logger.error(f"Inline autobc: {traceback.format_exc()}")
            return None
        results.append(
            InlineQueryResultArticle(
                title="Select Topic",
                input_message_content=InputTextMessageContent(caption),
                reply_markup=reply_markup,
            )
        )
        return results
    except Exception:
        logger.error(f"Inline autobc: {traceback.format_exc()}")
        return None


async def inline_info(results, inline):
    uniq = str(inline.query.split()[1])
    _id = inline.query.split()[2]
    try:
        message = next((obj for obj in get_objects() if id(obj) == int(_id)), None)
        if not message:
            return results

        client = message._client
        from_user = None
        from_user_id, from_user_name, user = Tools.extract_user(message)
        small_user = None
        full_user = None
        creation_date = "-"
        dc_id = "-"
        gbanned = False
        is_bot = False
        premium = False

        try:
            if user or isinstance(user, User):
                from_user = await client.invoke(
                    GetFullUser(id=(await client.resolve_peer(from_user_id)))
                )
                if from_user:
                    await client.unblock_user("creationdatebot")
                    xin = await client.resolve_peer("creationdatebot")
                    try:
                        created = await Tools.interact_with(
                            await client.send_message(
                                "creationdatebot", f"/id {user.id}"
                            )
                        )
                        creation_date = created.text
                    except Exception:
                        creation_date = "-"
                    Tools.interact_with_to_delete.clear()
                    small_user = from_user.users[0]
                    full_user = from_user.full_user
                    dc_id = getattr(small_user.photo, "dc_id", "-")
                    gbanned = small_user.id in await dB.get_list_from_var(
                        client.me.id, "GBANNED"
                    )
                    is_bot = small_user.bot
                    premium = small_user.premium
                    from_user = User._parse(client, small_user)
                    await client.invoke(
                        raw.functions.messages.DeleteHistory(
                            peer=xin, max_id=0, revoke=True
                        )
                    )
        except Exception:
            from_user = None

        if not from_user:
            try:
                from_user = await client.invoke(
                    GetFullChannel(channel=(await client.resolve_peer(from_user_id)))
                )
                small_user = from_user.chats[0]
                full_user = from_user.full_chat
                dc_id = getattr(full_user.chat_photo, "dc_id", "-")
                from_user = Chat._parse_channel_chat(client, small_user)
            except Exception:
                from_user = None

        if not from_user:
            return await message.reply(
                "**Gagal mengambil info. Silakan periksa kembali user atau chat target.**"
            )

        first_name = getattr(from_user, "title", getattr(from_user, "first_name", " "))
        last_name = getattr(from_user, "last_name", "")
        username = from_user.username or ""
        msg = ""

        if isinstance(from_user, User):
            msg += "<blockquote expandable><b>UserInfo:</b>\n"
            msg += f"   <b>name:</b> <b><a href='tg://user?id={from_user.id}'>{first_name} {last_name}</a></b>\n"
            msg += f"      <b>id:</b> <code>{from_user.id}</code>\n"
            msg += f"      <b>dc_id:</b> <code>{dc_id}</code>\n"
            msg += f"      <b>created_at:</b> <code>{creation_date}</code>\n"
            msg += f"      <b>is_bot:</b> <code>{is_bot}</code>\n"
            msg += f"      <b>is_gbanned:</b> <code>{gbanned}</code>\n"
            msg += f"      <b>is_premium:</b> <b>{premium}</b>\n"
            buttons = ikb(
                [
                    [
                        (
                            "User Link",
                            f"https://t.me/{username}" if username else from_user_id,
                            "url" if username else "user_id",
                        ),
                        ("User Bio", f"getbio_{from_user.id}"),
                    ],
                    [("Close", f"close inline_info {uniq} {_id}")],
                ]
            )
        elif isinstance(from_user, Chat):
            msg += "<blockquote expandable><b>ChatInfo:</b>\n"
            msg += f"   <b>name:</b> <b><a href='https://t.me/c/{full_user.id}'>{first_name}</a></b>\n"
            msg += f"      <b>dc_id:</b> <code>{dc_id}</code>\n"
            msg += f"      <b>id:</b> <code>{from_user.id}</code>\n"
            buttons = ikb(
                [
                    [
                        (
                            "Chat Link",
                            (
                                f"https://t.me/{username}"
                                if username
                                else f"https://t.me/c/{full_user.id}"
                            ),
                            "url",
                        ),
                        ("Chat Bio", f"getbio_{from_user.id}"),
                    ],
                    [("Close", f"close inline_info {uniq} {_id}")],
                ]
            )

        if getattr(full_user, "about", None):
            state.set(from_user.id, "bio", full_user.about)

        if getattr(full_user, "common_chats_count", None):
            msg += f"      <b>same_group:</b> <code>{full_user.common_chats_count}</code>\n"

        if isinstance(from_user, User) and message.chat.type in [
            enums.ChatType.SUPERGROUP,
            enums.ChatType.CHANNEL,
        ]:
            try:
                chat_member_p = await message.chat.get_member(small_user.id)
                joined_date = (
                    chat_member_p.joined_date or datetime.fromtimestamp(time())
                ).strftime("%d-%m-%Y %H:%M:%S")
                msg += f"      <b>joinned:</b> <code>{joined_date}</code>\n"
            except UserNotParticipant:
                pass

        if len(msg) < 334:
            polos = getattr(
                full_user, "settings", getattr(full_user, "available_reactions", None)
            )
            if polos:
                msg += f"      <b>reactions:</b> <code>{len(polos)}</code>\n"

        if getattr(full_user, "online_count", None):
            msg += f"      <b>online_count:</b> <code>{full_user.online_count}</code>\n"

        if getattr(full_user, "pinned_msg_id", None):
            url_pin = (
                f"tg://openmessage?user_id={full_user.id}&message_id={full_user.pinned_msg_id}"
                if isinstance(full_user, raw.types.UserFull)
                else f"https://t.me/c/{full_user.id}/{full_user.pinned_msg_id}"
            )
            msg += (
                f"      <b>pinned:</b> <b><a href='{url_pin}'>Pinned Message</a></b>\n"
            )

        if getattr(full_user, "linked_chat_id", None):
            msg += f"      <b>linked_chat:</b> <b><a href='https://t.me/c/{full_user.linked_chat_id}/1'>Linked Chat</a></b>\n"
        msg += "</blockquote>"
        results.append(
            InlineQueryResultArticle(
                title="Inline Info",
                input_message_content=InputTextMessageContent(msg),
                reply_markup=buttons,
            )
        )
        return results

    except Exception:
        logger.error(f"Inline info: {traceback.format_exc()}")


async def inline_chatai(results, inline):
    uniq = str(inline.query.split()[1])
    msg = "**Please choose model for AI:**"
    buttons = ikb(
        [
            [
                ("ChatGpt Normal", f"chatgpt_normal_{uniq}"),
                ("ChatGpt Audio", f"chatgpt_audio_{uniq}"),
            ],
            [("Close", f"close inline_chatai {uniq}")],
        ]
    )
    results.append(
        InlineQueryResultArticle(
            title="Inline Chat AI",
            input_message_content=InputTextMessageContent(msg),
            reply_markup=(buttons),
        )
    )
    return results


async def inline_gptaudio(results, inline):
    uniq = str(inline.query.split()[1])
    msg = "<b>Please select model first.</b>"
    models = [
        "alloy",
        "echo",
        "fable",
        "onyx",
        "nova",
        "shimmer",
        "coral",
        "verse",
        "ballad",
        "ash",
        "sage",
        "amuch",
        "dan",
        "elan",
    ]

    buttons = []
    row = []
    for idx, model in enumerate(models, 1):
        row.append(
            InlineKeyboardButton(
                model.capitalize(), callback_data=f"gptvoice_{model}_{uniq}"
            )
        )
        if idx % 3 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    results.append(
        InlineQueryResultArticle(
            title="GPT Voice Models",
            input_message_content=InputTextMessageContent(msg),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    )
    return results


async def inline_comic(results, inline):
    uniq = str(inline.query.split()[1])
    data = state.get(uniq, "comic")
    try:
        buttons = ikb([[("➡️ Next", f"restcomic_1_{uniq}")]])
        title = data[0].get("title")
        chapter = data[0].get("chapters", [{}])[0]
        episode = chapter.get("title", "-")
        date = chapter.get("date", "-")
        chapter_url = chapter.get("url", "")
        if "https://komiku.id" in chapter_url and not chapter_url.startswith(
            "https://komiku.id/"
        ):
            chapter_url = chapter_url.replace("https://komiku.id", "https://komiku.id/")

        judul = f"**Title:** {title}\n**Chapters:** {episode}\n**Link:** {chapter_url}\n**Uploaded:** {date}"
        results.append(
            InlineQueryResultArticle(
                input_message_content=InputTextMessageContent(judul),
                title="Inline Comic",
                reply_markup=buttons,
            )
        )
        return results
    except Exception:
        logger.error(f"Inline comic: {traceback.format_exc()}")


async def inline_donghua(results, inline):
    uniq = str(inline.query.split()[1])
    data = state.get(uniq, "donghua")
    try:
        buttons = ikb([[("➡️ Next", f"restdonghua_1_{uniq}")]])
        title = data[0].get("title")
        episode = data[0].get("episode")
        target = data[0].get("cover")
        url = data[0].get("url")
        judul = f"**Title:** {title}\n**Episode:** {episode}\n**Link:** {url}"
        results.append(
            InlineQueryResultPhoto(
                photo_url=target,
                caption=judul,
                title="Inline Donghua",
                reply_markup=buttons,
            )
        )
        return results
    except Exception:
        logger.error(f"Inline donghua: {traceback.format_exc()}")


async def inline_anime(results, inline):
    uniq = str(inline.query.split()[1])
    data = state.get(uniq, "anime")
    data = data["anime"]
    try:
        buttons = ikb(
            [
                [("➡️ Next", f"restanime_1_{uniq}")],
                [("❌ Close", f"close inline_anime {uniq}")],
            ]
        )
        title = data[0].get("title", "-")
        thumb = data[0].get("thumbnail", "-")
        episode = data[0].get("episode", "-")
        release = data[0].get("release", "-")
        link = data[0].get("link", "-")
        caption = f"""
**Title:** `{title}`
**Episode:** {episode}
**Release:** {release}
**Link:** <a href='{link}'>Here</a>
"""
        results.append(
            InlineQueryResultPhoto(
                photo_url=thumb,
                caption=caption,
                title="Inline Anime",
                reply_markup=buttons,
            )
        )
        return results
    except Exception:
        logger.error(f"Inline anime: {traceback.format_exc()}")


async def inline_news(results, inline):
    uniq = str(inline.query.split()[1])
    data = state.get(uniq, "news")
    try:
        buttons = ikb(
            [
                [("📮 Link", f"{data[0]['link']}", "url")],
                [("➡️ Next", f"news_1_{uniq}")],
            ]
        )
        date = data[0].get("time", "-")
        foto = data[0]["image_thumbnail"] or URL_LOGO
        content = data[0]["content"]
        clean_content = content[:500]
        judul = f"""
<blockquote expandable>
**Title:** {data[0]['title']}
**Uploaded:** {date}
**Content:** {clean_content}
</blockquote>
"""
        results.append(
            InlineQueryResultPhoto(
                photo_url=foto,
                caption=judul,
                title="Inline News",
                reply_markup=buttons,
            )
        )
        return results
    except Exception:
        logger.error(f"Inline news: {traceback.format_exc()}")


async def inline_spotify(results, inline):
    uniq = str(inline.query.split()[1])
    data = state.get(uniq, uniq)
    state.set(uniq, "fordlspotify", data[0]["track_url"])

    per_page = 5
    page = 0
    sliced = data[page * per_page : (page + 1) * per_page]

    caption = "<blockquote expandable><b>🎧 Spotify Results (Page 1)</b>\n\n"
    buttons = []
    for idx, audio in enumerate(sliced):
        caption += f"""<b>{idx + 1}. {audio['title']}</b>
🎤 {audio['artist']} | 💽 {audio['album']} | ⏱️ {audio['duration']}
📅 {audio['release_date']}
🔗 <a href="{audio['track_url']}">Spotify Link</a>\n"""
        buttons.append(
            [
                (
                    "⬇️ Download " + audio["title"][:20],
                    f"dlspot_{uniq}_{page * per_page + idx}",
                )
            ]
        )
    caption += "</blockquote>"
    total_pages = (len(data) + per_page - 1) // per_page
    nav_buttons = [(str(i + 1), f"nxtspotify_{i}_{uniq}") for i in range(total_pages)]
    buttons.append(nav_buttons)

    results.append(
        InlineQueryResultArticle(
            title="Spotify Results",
            description="Tap a button to download",
            input_message_content=InputTextMessageContent(
                caption, disable_web_page_preview=True
            ),
            reply_markup=ikb(buttons),
        )
    )
    return results


async def inline_apkan1(results, inline):
    uniq = str(inline.query.split()[1])
    data = state.get(uniq, uniq)
    if len(data) == 0:
        return results
    try:
        title = data[0].get("title")
        link = data[0].get("link")
        thumbnail = data[0].get("image")
        type = data[0].get("type")
        developer = data[0].get("developer")
        rating = data[0]["rating"]
        msg = f"""
**Title:** {title}
**Developer:** {developer}
**Rating:** {rating.get('value', '-')} | {rating.get('percentage', '-')}%
**Type:** {type}
"""
        buttons = ikb(
            [[("📮 Link", f"{link}", "url")], [("➡️ Next", f"an1cb_1_{uniq}")]]
        )
        results.append(
            InlineQueryResultPhoto(
                photo_url=thumbnail,
                caption=msg,
                title="Inline Apkinfo",
                reply_markup=buttons,
            )
        )
        return results
    except Exception:
        logger.error(f"Inline Apkan1: {traceback.format_exc()}")


async def inline_apkmoddy(results, inline):
    uniq = str(inline.query.split()[1])
    data = state.get(uniq, uniq)
    if len(data) == 0:
        return results
    try:
        title = data[0].get("title")
        link = data[0].get("link")
        thumbnail = data[0].get("icon")
        genre = data[0].get("genre")
        rating = data[0]["rating"]
        msg = f"""
**Title:** {title}
**Rating:** {rating.get('value', '-')} | {rating.get('percentage', '-')}%
**Genre:** {genre}
"""
        buttons = ikb(
            [[("📮 Link", f"{link}", "url")], [("➡️ Next", f"moddycb_1_{uniq}")]]
        )
        results.append(
            InlineQueryResultPhoto(
                photo_url=thumbnail,
                caption=msg,
                title="Inline Apkinfo",
                reply_markup=buttons,
            )
        )
        return results
    except Exception:
        logger.error(f"Inline Apkinfo: {traceback.format_exc()}")


async def inline_bola(resultss, inline_query):
    url = f"https://api.maelyn.sbs/api/jadwalbola?apikey={API_MAELYN}"
    result = await Tools.fetch.get(url)
    uniq = str(inline_query.query.split()[1])
    if result.status_code == 200:
        data = result.json()
        if data["status"] == "Success":
            buttons = []
            temp_row = []
            state.set(uniq, "jadwal_bola", data["result"])
            for liga_date in data["result"]:
                button = InlineKeyboardButton(
                    text=liga_date["LigaDate"],
                    callback_data=f"bola_matches {uniq} {liga_date['LigaDate']}",
                )
                temp_row.append(button)

                if len(temp_row) == 3:
                    buttons.append(temp_row)
                    temp_row = []

            if temp_row:
                buttons.append(temp_row)
            last_row = [
                InlineKeyboardButton(text="« Back", callback_data=f"bola_date {uniq}"),
                InlineKeyboardButton(
                    text="Close", callback_data=f"close inline_bola {uniq}"
                ),
            ]
            buttons.append(last_row)
            keyboard = InlineKeyboardMarkup(buttons)

            resultss.append(
                InlineQueryResultArticle(
                    title="Football Schedule",
                    reply_markup=keyboard,
                    input_message_content=InputTextMessageContent(
                        "<b>Select a date to view football matches:</b>"
                    ),
                )
            )
    return resultss


async def inline_cat(result, inline_query):
    uniq = str(inline_query.query.split()[1])
    buttons = ikb(
        [
            [("Refresh cat", f"refresh_cat_{uniq}")],
            [("Close", f"close inline_cat {uniq}")],
        ]
    )
    r = requests.get("https://api.thecatapi.com/v1/images/search")
    if r.status_code == 200:
        data = r.json()
        cat_url = data[0]["url"]
        if cat_url.endswith(".gif"):
            result.append(
                InlineQueryResultAnimation(
                    animation_url=cat_url,
                    title="cat Inline!",
                    reply_markup=buttons,
                    caption="<blockquote><b>Meow 😽</b></blockquote>",
                )
            )
        else:
            result.append(
                InlineQueryResultPhoto(
                    photo_url=cat_url,
                    title="cat Inline!",
                    reply_markup=buttons,
                    caption="<blockquote><b>Meow 😽</b></blockquote>",
                )
            )

    return result


async def inline_font(result, inline_query):
    get_id = str(inline_query.query.split()[1])

    keyboard = ButtonUtils.create_font_keyboard(query_fonts[0], get_id, current_batch=0)

    buttons = InlineKeyboardMarkup(keyboard)
    result.append(
        InlineQueryResultArticle(
            title="Font Inline!",
            reply_markup=buttons,
            input_message_content=InputTextMessageContent(
                "<blockquote><b>Please choice fonts:</b></blockquote>"
            ),
        )
    )
    return result


async def pmpermit_inline(result, inline_query):
    try:
        client = inline_query.from_user.id
        uniq = str(inline_query.query.split()[1])
        him = int(inline_query.query.split()[2])
        get_id = state.get(uniq, f"idm_{him}")
        message = [obj for obj in get_objects() if id(obj) == get_id][0]
        gtext = await dB.get_var(client, "PMTEXT")
        pm_text = gtext if gtext else DEFAULT_TEXT
        pm_warns = await dB.get_var(client, "PMLIMIT") or LIMIT
        Flood = state.get(client, him)
        teks, button = ButtonUtils.parse_msg_buttons(pm_text)
        button = await ButtonUtils.create_inline_keyboard(button, client)
        def_button = ikb(
            [
                [
                    (
                        f"You have a warning {Flood} of {pm_warns} !!",
                        f"pm_warn {client} {him}",
                        "callback_data",
                    )
                ]
            ]
        )
        if button:
            for row in def_button.inline_keyboard:
                button.inline_keyboard.append(row)
        else:
            button = def_button
        tekss = await Tools.escape_filter(message, teks, Tools.parse_words)
        media = await dB.get_var(client, "PMMEDIA")
        if media:
            file_id = str(media["file_id"])
            type = str(media["type"])
            type_mapping = {
                "photo": InlineQueryResultCachedPhoto,
                "video": InlineQueryResultCachedVideo,
                "animation": InlineQueryResultCachedAnimation,
                "audio": InlineQueryResultCachedDocument,
                "document": InlineQueryResultCachedDocument,
                "sticker": InlineQueryResultCachedPhoto,
                "voice": InlineQueryResultCachedVoice,
            }
            result_class = type_mapping[type]
            kwargs = {
                "id": str(uuid4()),
                "caption": tekss,
                "reply_markup": button,
            }
            if type == "photo":
                kwargs["photo_file_id"] = file_id
            elif type == "video":
                kwargs.update({"video_file_id": file_id, "title": "Video with Button"})
            elif type == "animation":
                kwargs["animation_file_id"] = file_id
            elif type == "audio":
                kwargs.update(
                    {"document_file_id": file_id, "title": "Document with Button"}
                )
            elif type == "document":
                kwargs.update(
                    {"document_file_id": file_id, "title": "Document with Button"}
                )
            elif type == "sticker":
                kwargs["photo_file_id"] = file_id
            elif type == "voice":
                kwargs.update({"voice_file_id": file_id, "title": "Voice with Button"})
            result.append(result_class(**kwargs))
        else:
            result.append(
                InlineQueryResultArticle(
                    title="PMPermit NOn-Media",
                    input_message_content=InputTextMessageContent(
                        tekss,
                        disable_web_page_preview=True,
                    ),
                    reply_markup=button,
                )
            )
        return result
    except Exception:
        logger.error(f"Pmpermit: {traceback.format_exc()}")
        raise


async def send_inline(result, _, user_id):
    try:
        _id = state.get(user_id, "inline_send")
        message = next((obj for obj in get_objects() if id(obj) == int(_id)), None)
        if message:
            button = message.reply_to_message.reply_markup
            caption = (
                message.reply_to_message.text or message.reply_to_message.caption or ""
            )
            entities = (
                message.reply_to_message.entities
                or message.reply_to_message.caption_entities
                or ""
            )
            if message.reply_to_message.media:
                client = message._client
                reply = message.reply_to_message
                copy = await reply.copy(bot.me.username)
                sent = await client.send_message(
                    bot.me.username, "/id send_media", reply_to_message_id=copy.id
                )
                await asyncio.sleep(1)
                await sent.delete()
                await copy.delete()
                data = state.get(user_id, "send_media")
                file_id = str(data["file_id"])
                type = str(data["type"])
                type_mapping = {
                    "photo": InlineQueryResultCachedPhoto,
                    "video": InlineQueryResultCachedVideo,
                    "animation": InlineQueryResultCachedAnimation,
                    "audio": InlineQueryResultCachedDocument,
                    "document": InlineQueryResultCachedDocument,
                    "sticker": InlineQueryResultCachedSticker,
                    "voice": InlineQueryResultCachedVoice,
                }
                result_class = type_mapping[type]
                kwargs = {
                    "id": str(uuid4()),
                    "caption": caption,
                    "reply_markup": button,
                    "caption_entities": entities,
                }

                if type == "photo":
                    kwargs["photo_file_id"] = file_id
                elif type == "video":
                    kwargs.update(
                        {"video_file_id": file_id, "title": "Video with Button"}
                    )
                elif type == "animation":
                    kwargs["animation_file_id"] = file_id
                elif type == "audio":
                    kwargs.update(
                        {"document_file_id": file_id, "title": "Document with Button"}
                    )
                elif type == "document":
                    kwargs.update(
                        {"document_file_id": file_id, "title": "Document with Button"}
                    )
                elif type == "sticker":
                    kwargs["sticker_file_id"] = file_id
                elif type == "voice":
                    kwargs.update(
                        {"voice_file_id": file_id, "title": "Voice with Button"}
                    )

                result.append(result_class(**kwargs))
            else:
                result.append(
                    InlineQueryResultArticle(
                        id=str(uuid4()),
                        title="Send Inline!",
                        reply_markup=button,
                        input_message_content=InputTextMessageContent(
                            caption, entities=entities
                        ),
                    )
                )
        return result
    except Exception as er:
        logger.error(f"ERROR: {traceback.format_exc()}")


async def button_inline(result, _, user_id):
    try:
        data = state.get(user_id, "button")
        text, button = ButtonUtils.parse_msg_buttons(data)
        if button:
            button = await ButtonUtils.create_inline_keyboard(button, user_id)

        data2 = state.get(user_id, "button_media")
        if not data2:
            result.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="Text Button!",
                    input_message_content=InputTextMessageContent(
                        text, disable_web_page_preview=True
                    ),
                    reply_markup=button,
                )
            )
        else:
            file_id = str(data2["file_id"])
            type = str(data2["type"])
            type_mapping = {
                "photo": InlineQueryResultCachedPhoto,
                "video": InlineQueryResultCachedVideo,
                "animation": InlineQueryResultCachedAnimation,
                "audio": InlineQueryResultCachedDocument,
                "document": InlineQueryResultCachedDocument,
                "sticker": InlineQueryResultCachedSticker,
                "voice": InlineQueryResultCachedVoice,
            }

            if type in type_mapping:
                result_class = type_mapping[type]
                kwargs = {
                    "id": str(uuid4()),
                    "caption": text,
                    "reply_markup": button,
                }

                if type == "photo":
                    kwargs["photo_file_id"] = file_id
                elif type == "video":
                    kwargs.update(
                        {"video_file_id": file_id, "title": "Video with Button"}
                    )
                elif type == "animation":
                    kwargs["animation_file_id"] = file_id
                elif type == "audio":
                    kwargs.update(
                        {"document_file_id": file_id, "title": "Document with Button"}
                    )
                elif type == "document":
                    kwargs.update(
                        {"document_file_id": file_id, "title": "Document with Button"}
                    )
                elif type == "sticker":
                    kwargs["sticker_file_id"] = file_id
                elif type == "voice":
                    kwargs.update(
                        {"voice_file_id": file_id, "title": "Voice with Button"}
                    )

                result.append(result_class(**kwargs))

        return result
    except Exception as er:
        logger.error(f"ERROR: {traceback.format_exc()}")


async def get_inline_help(result, inline_query):
    user_id = inline_query.from_user.id
    prefix = navy.get_prefix(user_id)
    plan = await dB.get_var(user_id, "plan")
    plan_teks = None
    if plan == "is_pro":
        visible_helpable = HELPABLE
        plan_teks = "Pro"
    elif plan == "basic":
        visible_helpable = {
            name: data for name, data in HELPABLE.items() if not data["is_pro"]
        }
        plan_teks = "Basic"
    elif plan == "lite":
        visible_helpable = {
            name: data
            for name, data in HELPABLE.items()
            if not data["is_pro"] and not data["is_basic"]
        }
        plan_teks = "Lite"
    text_help = (
        await dB.get_var(user_id, "text_help")
        or f"**🤖 {BOT_NAME} by {USENAME_OWNER}**"
    )
    full = f"<a href=tg://user?id={inline_query.from_user.id}>{inline_query.from_user.first_name} {inline_query.from_user.last_name or ''}</a>"
    msg = """
<b>Inline Help
    Plan: <b>{}</b> 
    Prefixes: <code>{}</code>
    Plugins: <code>{}</code>
    {}</b>
<blockquote>{}</blockquote>""".format(
        plan_teks,
        " ".join(prefix),
        len(visible_helpable),
        full,
        text_help,
    )
    result.append(
        InlineQueryResultArticle(
            title="Help Menu!",
            description=" Command Help",
            thumb_url=URL_LOGO,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(0, visible_helpable, "help")
            ),
            input_message_content=InputTextMessageContent(msg),
        )
    )
    return result


async def alive_inline(result, inline_query):
    uniq = str(inline_query.query.split()[1])
    self = inline_query.from_user.id
    pmper = None
    status = None
    start = datetime.now()
    ping = (datetime.now() - start).microseconds / 1000
    upnya = await get_time((time() - start_time))
    me = next((x for x in navy._ubot), None)
    try:
        peer = navy._get_my_peer[self]
        users = len(peer["private"])
        group = len(peer["group"])
    except Exception:
        users = random.randrange(await me.get_dialogs_count())
        group = random.randrange(await me.get_dialogs_count())
    await me.invoke(Ping(ping_id=0))
    seles = await dB.get_list_from_var(bot.me.id, "SELLER")
    if self in SUDO_OWNERS:
        status = "[Admins]"
    elif self in seles:
        status = "[Seller]"
    else:
        status = "[Costumer]"
    cekpr = await dB.get_var(self, "PMPERMIT")
    if cekpr:
        pmper = "enable"
    else:
        pmper = "disable"
    get_exp = await dB.get_expired_date(self)
    exp = get_exp.strftime("%d-%m-%Y")
    plan = await dB.get_var(self, "plan")
    is_pro = "pro" if plan == "is_pro" else plan
    txt = f"""
<b>{BOT_NAME}</b>
    <b>status:</b> {status} 
      <b>dc_id:</b> <code>{me.me.dc_id}</code>
      <b>plan_ubot:</b> **{is_pro}**
      <b>ping_dc:</b> <code>{str(ping).replace('.', ',')} ms</code>
      <b>anti_pm:</b> <code>{pmper}</code>
      <b>peer_users:</b> <code>{users} users</code>
      <b>peer_group:</b> <code>{group} group</code>
      <b>peer_ubot:</b> <code>{len(navy._ubot)} ubot</code>
      <b>uptime:</b> <code>{upnya}</code>
      <b>expires:</b> <code>{exp}</code>
"""
    msge = f"<blockquote>{txt}</blockquote>"
    button = ikb([[("Close", f"close alive {uniq}")]])
    cekpic = await dB.get_var(self, "ALIVE_PIC")
    if not cekpic:
        result.append(
            InlineQueryResultArticle(
                title=BOT_NAME,
                description="Get Alive Of Bot.",
                input_message_content=InputTextMessageContent(msge),
                thumb_url=URL_LOGO,
                reply_markup=button,
            )
        )
    else:
        media = (
            InlineQueryResultVideo
            if cekpic.endswith(".mp4")
            else InlineQueryResultPhoto
        )
        url_ling = (
            {"video_url": cekpic, "thumb_url": cekpic}
            if cekpic.endswith(".mp4")
            else {"photo_url": cekpic}
        )
        result.append(
            media(
                **url_ling,
                title=BOT_NAME,
                description="Get Alive Of Bot.",
                thumb_url=URL_LOGO,
                caption=msge,
                reply_markup=button,
            )
        )
    return result


async def get_inline_note(result, inline_query):
    uniq = str(inline_query.query.split()[1])
    note = str(inline_query.query.split()[2])
    logger.info(f"Data notes: {note}")
    gw = inline_query.from_user.id
    _id = state.get(gw, "in_notes")
    message = next((obj for obj in get_objects() if id(obj) == int(_id)), None)
    noteval = await dB.get_var(gw, note, "notes")
    if not noteval:
        return
    btn_close = ikb([[("Close", f"close get_note {uniq} {note}")]])
    state.set("close_notes", "get_note", btn_close)
    try:
        tks = noteval["result"].get("text")
        type = noteval["type"]
        file_id = noteval["file_id"]
        note, button = ButtonUtils.parse_msg_buttons(tks)
        teks = await Tools.escape_filter(message, note, Tools.parse_words)
        button = await ButtonUtils.create_inline_keyboard(button, gw)
        for row in btn_close.inline_keyboard:
            button.inline_keyboard.append(row)
        if type != "text":
            type_mapping = {
                "photo": InlineQueryResultCachedPhoto,
                "video": InlineQueryResultCachedVideo,
                "animation": InlineQueryResultCachedAnimation,
                "audio": InlineQueryResultCachedDocument,
                "document": InlineQueryResultCachedDocument,
                "sticker": InlineQueryResultCachedSticker,
                "voice": InlineQueryResultCachedVoice,
            }
            result_class = type_mapping[type]
            kwargs = {
                "id": str(uuid4()),
                "caption": teks,
                "reply_markup": button,
                "parse_mode": enums.ParseMode.HTML,
            }

            if type == "photo":
                kwargs["photo_file_id"] = file_id
            elif type == "video":
                kwargs.update({"video_file_id": file_id, "title": "Video with Button"})
            elif type == "animation":
                kwargs["animation_file_id"] = file_id
            elif type == "audio":
                kwargs.update(
                    {"document_file_id": file_id, "title": "Document with Button"}
                )
            elif type == "document":
                kwargs.update(
                    {"document_file_id": file_id, "title": "Document with Button"}
                )
            elif type == "sticker":
                kwargs["sticker_file_id"] = file_id
            elif type == "voice":
                kwargs.update({"voice_file_id": file_id, "title": "Voice with Button"})

            result.append(result_class(**kwargs))
        else:
            result.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="Send Inline!",
                    reply_markup=button,
                    input_message_content=InputTextMessageContent(
                        teks,
                        parse_mode=enums.ParseMode.HTML,
                    ),
                )
            )
        return result
    except Exception:
        logger.error(f"Error notes: {traceback.format_exc()}")


async def inline_chord(results, inline):
    try:
        uniq = str(inline.query.split()[1])
    except IndexError:
        return results

    data = state.get(uniq, "chord") or []
    if not data:
        return results

    caption = f"<blockquote expandable><b>🎸 Chord Results</b>\n\n"
    for idx, song in enumerate(data):
        caption += (
            f"<b>{idx + 1}. {song['title']}</b>\n"
            f"🎤 {song['artist']}\n"
            f"🔗 <a href=\"{song['link']}\">Open Chord</a>\n\n"
        )
    caption += "</blockquote>"

    buttons = ButtonUtils.build_buttons(data, uniq, "viewchord_", "inline_chord")
    results.append(
        InlineQueryResultArticle(
            title="🎸 Inline Chord Result",
            input_message_content=InputTextMessageContent(
                caption, disable_web_page_preview=True
            ),
            reply_markup=buttons,
        )
    )
    return results


async def inline_afk(result, inline_query):
    user_id = inline_query.from_user.id
    _id = state.get(user_id, "afk")
    message = next((obj for obj in get_objects() if id(obj) == int(_id)), None)
    data_afk = await dB.get_var(user_id, "AFK")
    if not data_afk:
        return
    try:
        text = data_afk["result"].get("text")
        type = data_afk["type"]
        file_id = data_afk["file_id"]
        one, button = ButtonUtils.parse_msg_buttons(text)
        teks = await Tools.escape_filter(message, one, Tools.parse_words)
        button = await ButtonUtils.create_inline_keyboard(button)
        if type != "text":
            type_mapping = {
                "photo": InlineQueryResultCachedPhoto,
                "video": InlineQueryResultCachedVideo,
                "animation": InlineQueryResultCachedAnimation,
                "audio": InlineQueryResultCachedDocument,
                "document": InlineQueryResultCachedDocument,
                "sticker": InlineQueryResultCachedSticker,
                "voice": InlineQueryResultCachedVoice,
            }
            result_class = type_mapping[type]
            kwargs = {
                "id": str(uuid4()),
                "caption": teks,
                "reply_markup": button,
                "parse_mode": enums.ParseMode.HTML,
            }

            if type == "photo":
                kwargs["photo_file_id"] = file_id
            elif type == "video":
                kwargs.update({"video_file_id": file_id, "title": "Video with Button"})
            elif type == "animation":
                kwargs["animation_file_id"] = file_id
            elif type == "audio":
                kwargs.update(
                    {"document_file_id": file_id, "title": "Document with Button"}
                )
            elif type == "document":
                kwargs.update(
                    {"document_file_id": file_id, "title": "Document with Button"}
                )
            elif type == "sticker":
                kwargs["sticker_file_id"] = file_id
            elif type == "voice":
                kwargs.update({"voice_file_id": file_id, "title": "Voice with Button"})

            result.append(result_class(**kwargs))
        else:
            result.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="AFK Inline!",
                    reply_markup=button,
                    input_message_content=InputTextMessageContent(
                        teks,
                        parse_mode=enums.ParseMode.HTML,
                    ),
                )
            )
        return result
    except Exception:
        logger.error(f"Error afk: {traceback.format_exc()}")


async def inline_bmkg(results, inline):
    try:
        uniq = str(inline.query.split()[1])
        data_result = state.get(uniq, uniq)
        if not data_result:
            return results

        auto = data_result.get("auto", {}).get("Infogempa", {}).get("gempa", {})
        terkini = data_result.get("terkini", {}).get("Infogempa", {}).get("gempa", [])

        text = f"""
<blockquote expandable>
<b>🔔 #Gempa_Otomatis_Terbaru</b>

📅 <b>Tanggal:</b> <code>{auto.get('Tanggal', '-')}</code>
🕒 <b>Jam:</b> <code>{auto.get('Jam', '-')}</code>
📍 <b>Lokasi:</b> <code>{auto.get('Wilayah', '-')}</code>
📌 <b>Koordinat:</b> <code>{auto.get('Coordinates', '-')}</code>
💥 <b>Magnitudo:</b> <code>{auto.get('Magnitude', '-')}</code>
📏 <b>Kedalaman:</b> <code>{auto.get('Kedalaman', '-')}</code>
🌊 <b>Potensi:</b> <code>{auto.get('Potensi', '-')}</code>
😵 <b>Dirasakan:</b> <code>{auto.get('Dirasakan', '-')}</code>
</blockquote>
"""
        per_page = 5
        page = 0
        sliced = terkini[page * per_page : (page + 1) * per_page]
        total_pages = (len(terkini) + per_page - 1) // per_page

        buttons = []
        for idx, item in enumerate(sliced):
            judul = f"{item['Tanggal']} {item['Magnitude']} M - {item['Wilayah'][:20]}"
            callback_data = f"nxtbmkg_{uniq}_{page * per_page + idx}"
            buttons.append([("⬇️ " + judul, callback_data)])

        nav_buttons = [
            (str(i + 1), f"viewgempa_{i}_{uniq}") for i in range(total_pages)
        ]
        buttons.append(nav_buttons)

        results.append(
            InlineQueryResultArticle(
                title="🔴 Gempa Terkini (Auto)",
                description="Gempa terbaru dari BMKG dengan tombol navigasi.",
                input_message_content=InputTextMessageContent(
                    text,
                    disable_web_page_preview=True,
                ),
                reply_markup=ikb(buttons),
            )
        )

        return results

    except Exception:
        print(traceback.format_exc())
        return results


async def inline_youtube(results, inline):
    uniq = str(inline.query.split()[1])
    data = state.get(uniq, uniq)
    state.set(uniq, "fordlyt", data[0]["url"])
    per_page = 5
    page = 0
    sliced = data[page * per_page : (page + 1) * per_page]

    caption = "<blockquote expandable><b>🎧 Youtube Results (Page 1)</b>\n"
    buttons = []
    for idx, audio in enumerate(sliced):
        caption += f"""
<b>{idx + 1}. 💽 {audio['title']}</b>
🔗 <a href="{audio['url']}">Youtube Link</a>\n"""
        buttons.append(
            [
                (
                    "⬇️ Download " + audio["title"][:20],
                    f"dlytsearch_{uniq}_{page * per_page + idx}",
                )
            ]
        )
    caption += "</blockquote>"
    total_pages = (len(data) + per_page - 1) // per_page
    nav_buttons = [(str(i + 1), f"nxtytsearch_{i}_{uniq}") for i in range(total_pages)]
    buttons.append(nav_buttons)

    results.append(
        InlineQueryResultArticle(
            title="Youtube Results",
            description="Tap a button to download",
            input_message_content=InputTextMessageContent(
                caption, disable_web_page_preview=True
            ),
            reply_markup=ikb(buttons),
        )
    )
    return results
