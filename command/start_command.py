import asyncio
import random

from pyrogram import enums

from clients import bot
from config import KYNAN, LOG_SELLER, SUDO_OWNERS
from database import dB, state
from helpers import Basic_Effect, ButtonUtils, Message, Tools, no_commands
from logs import logger

funny_stick = [
    "CAACAgUAAxkBAAEEQ95ooL7ElYynWeMWqkw_alRBDk64cAACwRkAAocNCVUu77XVdoCEFR4E",
    "CAACAgUAAxkBAAEEQ-NooL7f5uxTwS7cvl8W6da9dL96bgACyRYAAq2ZCFVissEM8Qs2Jh4E",
    "CAACAgUAAxkBAAEEQ-ZooL74f-RfvnekTap8R2RcQr3OnwAC5hUAAqeuAAFV8v6_dyvy5SYeBA",
    "CAACAgUAAxkBAAEEQ-looL8AAb9KDs4GrcorBP72mqchDwIAAgkZAAI7HwABVWXxfagNSrARHgQ",
    "CAACAgUAAxkBAAEEQ-xooL8FDx8dD1NKLLA5nYDDs5d25AACgBoAAgNxCVWg-3RYMtryOh4E",
    "CAACAgUAAxkBAAEEQ-9ooL8eWprEDX0lnOj7fuPrr55CXQACVBgAAmcBAAFVq3-1pKGczsAeBA",
    "CAACAgUAAxkBAAEEQ_NooL8vZhSqcJljKu9MVSQ2FjJp0gACPBUAAnwmCFXgvfeUg9bhMx4E",
    "CAACAgUAAxkBAAEEQ_ZooL84KQAB2lZPOUM39nj5GAwOPZMAAjQZAALswwABVYB3QyArOvGoHgQ",
    "CAACAgUAAxkBAAEEQ_looL89u67UG72ox2F4-IiJmdYKGwACjBcAAp_ZCVWljJ-1AbASTh4E",
    "CAACAgUAAxkBAAEEQ_1ooL9ERfaGqju9LHf0Oz5AuzqTFAACCBgAAoekCFUF1BsdPoXBsh4E",
    "CAACAgUAAxkBAAEERAABaKC_SuCiBzBsJj1sBsHQqRLmJHcAAg8hAAK2MQlVqD3ucUB7VqseBA",
]


async def gen_image(client):
    image = None
    file_id = await dB.get_var(client.me.id, "IMAGE_START")
    if not file_id:
        return None

    if file_id.startswith("AgAC"):
        image = {"photo": file_id}
    elif file_id.startswith("BAAC"):
        image = {"video": file_id}
    elif file_id.startswith("CgAC"):
        image = {"animation": file_id}
    else:
        print(f"Unknown file ID prefix: {file_id[:4]}")
        return None

    return image


async def setimg_start(client, message):
    user = message.from_user if message.from_user else message.sender_chat
    if user.id not in KYNAN:
        return
    if message.reply_to_message:
        proses = await message.reply("<blockquote>**Tunggu sebentar..**</blockquote>")
        reply = message.reply_to_message
        if not reply.media:
            return await proses.edit(
                "<blockquote>**Silahkan balas ke pesan foto atau video**</blockquote>"
            )
        file_id = Tools.get_file_id(reply).get("file_id")
        await dB.set_var(client.me.id, "IMAGE_START", file_id)
        return await proses.edit(
            f"<blockquote>**Berhasil mengatur media start ke: <a href='{reply.link}'>pesan ini</a>**</blockquote>",
            disable_web_page_preview=True,
        )
    else:
        if len(message.command) == 2:
            args = message.command[1]
            if args in ["off", "disable"]:
                await dB.remove_var(client.me.id, "IMAGE_START")
                return await message.reply(
                    "<blockquote>**Media start dinon-aktifkan**</blockquote>"
                )
            else:
                return await message.reply(
                    "<blockquote>**Silahkan balas ke media jika ingin mengatur pesan start media, atau ketik `/setimg off` untuk menon-aktifkan pesan media start.**</blockquote>"
                )
        else:
            return await message.reply(
                "<blockquote>**Silahkan balas ke media jika ingin mengatur pesan start media, atau ketik `/setimg off` untuk menon-aktifkan pesan media start.**</blockquote>"
            )


async def setads_bot(client, message):
    user = message.from_user if message.from_user else message.sender_chat
    if user.id not in KYNAN:
        return
    if not message.reply_to_message:
        return await message.reply("**Silahkan balas ke teks**")
    proses = await message.reply("**Tunggu sebentar..**")
    reply = message.reply_to_message
    text = reply.text or reply.caption or ""
    await dB.set_var(client.me.id, "ads", text)
    return await proses.edit(
        f"**Pesan ads berhasil diatur ke: <a href='{reply.link}'>pesan ini</a>**"
    )


async def start_home(client, message):
    if message.chat.type != enums.ChatType.PRIVATE:
        return
    broadcast = await dB.get_list_from_var(client.me.id, "BROADCAST")
    user = message.from_user
    if user.id not in broadcast:
        await dB.add_to_var(client.me.id, "BROADCAST", user.id)
    stick = await message.reply_sticker(random.choice(funny_stick))
    await asyncio.sleep(1)
    await stick.delete()
    image_start = await gen_image(client)
    if message.from_user.id in SUDO_OWNERS:
        buttons = ButtonUtils.start_menu(is_admin=True)
    else:
        buttons = ButtonUtils.start_menu(is_admin=False)
        sender_id = message.from_user.id
        sender_mention = message.from_user.mention
        sender_name = message.from_user.first_name
        await client.send_message(
            LOG_SELLER,
            f"<b>User: {sender_mention}\nID: `{sender_id}`\nName: {sender_name}\nHas started your bot.</b>",
        )
    text = await Message.welcome_message(client, message)
    if image_start:
        if "video" in image_start:
            return await message.reply_video(
                video=image_start["video"],
                caption=text,
                reply_markup=buttons,
                effect_id=random.choice(Basic_Effect),
            )
        elif "animation" in image_start:
            return await message.reply_animation(
                animation=image_start["animation"],
                caption=text,
                reply_markup=buttons,
                effect_id=random.choice(Basic_Effect),
            )
        elif "photo" in image_start:
            return await message.reply_photo(
                photo=image_start["photo"],
                caption=text,
                reply_markup=buttons,
                effect_id=random.choice(Basic_Effect),
            )
    else:
        return await message.reply(
            text=text,
            reply_markup=buttons,
            disable_web_page_preview=True,
            effect_id=random.choice(Basic_Effect),
        )


async def button_bot(client, message):
    link = message.text.split(None, 1)[1]
    tujuan, _id = Tools.extract_ids_from_link(link)
    txt = state.get(message.from_user.id, "edit_reply_markup")
    teks, button = ButtonUtils.parse_msg_buttons(txt)
    if button:
        button = await ButtonUtils.create_inline_keyboard(button)
    return await client.edit_message_reply_markup(
        chat_id=tujuan, message_id=_id, reply_markup=button
    )


async def getid_bot(client, message):
    if len(message.command) < 2:
        return
    query = message.text.split()[1]
    try:
        reply = message.reply_to_message
        media = Tools.get_file_id(reply)
        data = {"file_id": media["file_id"], "type": media["message_type"]}
        state.set(message.from_user.id, query, data)
        return
    except Exception as er:
        logger.error(f"{str(er)}")


async def request_bot(client, message):
    user_id = message.from_user.id
    if not message.reply_to_message:
        reply_text = (
            "<b>English:</b> Please use the /request command by replying to a text message or media with a caption. And explain the features you want in detail to make it easier for the admin.\n\n"
            "<b>Indonesia:</b> Silahkan gunakan perintah /request dengan cara membalas pesan teks atau media dengan caption. Serta jelaskan fitur yang anda inginkan dengan detail agar memudahkan admin."
        )
        return await message.reply(reply_text)

    forward = await client.forward_messages(
        chat_id=LOG_SELLER,
        from_chat_id=message.chat.id,
        message_ids=message.reply_to_message.id,
    )
    await dB.set_var(forward.id, f"REQUEST_{forward.id}", user_id)
    return await message.reply(
        "<b>English:</b> Your report has been successfully submitted. Please wait for a response from the admin.\n\n"
        "<b>Indonesia:</b> Laporan kamu berhasil dikirimkan. Silahkan tunggu jawaban dari admin."
    )


async def lapor_bug(client, message):
    if client.me.id != bot.id:
        return
    user_id = message.from_user.id
    if not message.reply_to_message:
        reply_text = (
            "<b>English:</b> Please use the /bug command while replying to error text messages or media messages with captions.\n\n"
            "<b>Indonesia:</b> Silahkan gunakan perintah /bug dengan cara membalas pesan teks eror atau pesan media dengan caption."
        )
        return await message.reply(reply_text)
    forward = await client.forward_messages(
        chat_id=LOG_SELLER,
        from_chat_id=message.chat.id,
        message_ids=message.reply_to_message.id,
    )
    await dB.set_var(forward.id, f"BUG_{forward.id}", user_id)

    return await message.reply(
        "<b>English:</b> Your report has been successfully submitted. Please wait for a response from the admin.\n\n"
        "<b>Indonesia:</b> Laporan kamu berhasil dikirimkan. Silahkan tunggu jawaban dari admin."
    )


async def incoming_message(client, message):
    if message.chat.type != enums.ChatType.PRIVATE:
        return
    if message.sticker:
        return
    text = message.text or message.caption or ""
    if (
        text
        and text.startswith("/")
        or text in no_commands
        or not text.startswith("#ask")
    ):
        return
    user_id = message.from_user.id
    forward = await client.forward_messages(
        chat_id=LOG_SELLER, from_chat_id=message.chat.id, message_ids=message.id
    )
    await dB.set_var(forward.id, f"FORWARD_{forward.id}", user_id)


async def outgoing_reply(client, message):
    rep = message.reply_to_message
    if not rep:
        return
    for prefix in ("REQUEST_", "BUG_", "FORWARD_"):
        user_id = await dB.get_var(rep.id, f"{prefix}{rep.id}")
        if user_id:
            return await client.copy_message(
                chat_id=user_id, from_chat_id=message.chat.id, message_id=message.id
            )


async def back_home(client, callback):
    await callback.message.delete()
    if await dB.get_var(callback.from_user.id, "is_bot"):
        await dB.remove_var(callback.from_user.id, "is_bot")
        await dB.remove_var(callback.from_user.id, "is_bot_pro")
    broadcast = await dB.get_list_from_var(client.me.id, "BROADCAST")
    user = callback.from_user
    if user.id not in broadcast:
        await dB.add_to_var(client.me.id, "BROADCAST", user.id)
    if callback.from_user.id in SUDO_OWNERS:
        buttons = ButtonUtils.start_menu(is_admin=True)
    else:
        buttons = ButtonUtils.start_menu(is_admin=False)
    text = await Message.welcome_message(client, callback.message)
    return await client.send_message(
        user.id,
        text=text,
        reply_markup=buttons,
        disable_web_page_preview=True,
    )
