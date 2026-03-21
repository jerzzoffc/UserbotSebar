import asyncio
import re
import time
import traceback
from gc import get_objects

import requests
import wget
from pyrogram import enums, raw
from pyrogram.errors import FloodPremiumWait, FloodWait, MessageNotModified
from pyrogram.helpers import ikb
from pyrogram.types import InlineKeyboardButton as Ikb
from pyrogram.types import (InlineKeyboardMarkup, InputMediaAnimation,
                            InputMediaAudio, InputMediaDocument,
                            InputMediaPhoto, InputMediaVideo)
from pyrogram.utils import unpack_inline_message_id
from pytz import timezone

from clients import bot, navy
from config import (API_MAELYN, BOT_NAME, COPY_ID, HELPABLE, LOG_SELLER,
                    SUDO_OWNERS, USENAME_OWNER)
from database import dB, state
from helpers import (ButtonUtils, Emoji, Message, Spotify, Tools, gens_font,
                     paginate_modules, query_fonts, youtube)
from logs import logger

from .pmpermit_command import LIMIT

MESSAGE_DICT = {}
CONVERSATIONS = {}


top_text = """
<b>Inline Help
    Plan: <b>{}</b>
    Prefixes: <code>{}</code>
    Plugins: <code>{}</code>
    {}</b>
<blockquote>{}</blockquote>"""

text_markdown = "**To view markdown format please click on the button below.**"

text_formatting = """
> **Markdown Formatting**
> Anda dapat memformat pesan Anda menggunakan **tebal**, _miring_, --garis bawah--, ~~coret~~, dan banyak lagi.
>
> `<code>kata kode</code>`: Tanda kutip terbalik digunakan buat font monospace. Ditampilkan sebagai: `kata kode`.
>
> `<i>miring</i>`: Garis bawah digunakan buat font miring. Ditampilkan sebagai: __kata miring__.
>
> `<b>tebal</b>`: Asterisk digunakan buat font tebal. Ditampilkan sebagai: **kata tebal**.
>
> `<u>garis bawah</u>`: Buat membuat teks --garis bawah--.
>
> `<strike>coret</strike>`: Tilda digunakan buat strikethrough. Ditampilkan sebagai: ~~coret~~.
>
> `<spoiler>spoiler</spoiler>`: Garis vertikal ganda digunakan buat spoiler. Ditampilkan sebagai: ||spoiler||.
>
> `[hyperlink](contoh)`: Ini adalah pemformatan yang digunakan buat hyperlink.
>
> `<blockquote>teks quote</blockquote>`: Ini adalah pemformatan untuk > teks quote >
>
> `Hallo Disini [Tombol 1|https://link.com]` : Ini adalah pemformatan yang digunakan membuat tombol.
> `Halo Disini [Tombol 1|t.me/kynansupport][Tombol 2|t.me/kontenfilm|same]` : Ini akan membuat tombol berdampingan.
>
> Anda juga bisa membuat tombol callback_data dengan diawal tanda `cb_`
> Jika ingin membuat copy text gunakan Halo Disini `[Click To Copy|copy:1234]`
> Contoh callback `Halo Disini [Tombol 1|data][Tombol 2|data|same]`
>
> Anda juga dapat membuat tombol callback answer dengan diawal tanda `alert:`
> Contoh callback answer`Halo Disini [Tombol 1|alert:Yang klik jelek][Tombol 2|alert:Jangan diklik Tapi boong|same]`
>
> Anda juga dapat membuat teks collapsed dengan button
> Contoh `<blockquote expandable>Aku adalah NavyUbot yang dikembang oleh @kenpanan dan aku adalah userbot generasi ke 3 setelah KN-Userbot Aku lebih sempurna dari generasi sebelumnya karna aku dibuat dengan memprioritaskan flexibilitas</blockquote> [Owner|https://t.me/kenapanan]`
>
"""

text_fillings = "<blockquote expandable><b>Fillings</b>\n\nAnda juga dapat menyesuaikan isi pesan Anda dengan data kontekstual. Misalnya, Anda bisa menyebut nama pengguna dalam pesan selamat datang, atau menyebutnya dalam filter!\n\n<b>Isian yang didukung:</b>\n\n<code>{first}</code>: Nama depan pengguna.\n<code>{last}</code>: Nama belakang pengguna.\n<code>{fullname}</code>: Nama lengkap pengguna.\n<code>{username}</code>: Nama pengguna pengguna. Jika mereka tidak memiliki satu, akan menyebutkan pengguna tersebut.\n<code>{mention}</code>: Menyebutkan pengguna dengan nama depan mereka.\n<code>{id}</code>: ID pengguna.\n<code>{date}</code>: Tanggal, <code>{day}</code>: hari, <code>{month}</code>: bulan, <code>{year}</code>: tahun, <code>{hour}</code>: jam, <code>{minute}</code>: menit.</blockquote>"


async def callback_alert(_, callback_query):
    uniq = callback_query.data.split("_")[1]
    alert_text = await dB.get_var(uniq, f"{uniq}")
    if len(alert_text) > 200:
        return await callback_query.answer(
            "Alert text is too long, please keep it under 200 characters.",
            show_alert=True,
        )
    if r"\n" in alert_text:
        alert_text = alert_text.replace(r"\n", "\n")
    return await callback_query.answer(text=alert_text, show_alert=True)


async def cb_markdown(_, callback_query):
    await callback_query.answer()
    data = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id
    cekpic = await dB.get_var(user_id, "HELP_LOGO")
    costum_cq = (
        callback_query.edit_message_caption
        if cekpic
        else callback_query.edit_message_text
    )
    full = f"<a href=tg://user?id={callback_query.from_user.id}>{callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}</a>"
    costum_text = "caption" if cekpic else "text"
    prev_page_num = state.get(user_id, "prev_page_num")
    if data == "format":
        # text = f"<blockquote expandable>{text_formatting.strip()}</blockquote>"
        try:
            button = ikb(
                [
                    [
                        ("Formatting", "markdown_format", "callback_data"),
                        ("Fillings", "markdown_fillings", "callback_data"),
                    ],
                    [
                        ("🔙 Back", f"help_back({prev_page_num})"),
                    ],
                ]
            )
            return await costum_cq(
                **{costum_text: text_formatting.strip()},
                reply_markup=button,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.MARKDOWN,
            )

        except (FloodWait, FloodPremiumWait) as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return
    elif data == "fillings":
        text = f"<blockquote expandable>{text_fillings.strip()}</blockquote>"
        try:
            button = ikb(
                [
                    [
                        ("Formatting", "markdown_format", "callback_data"),
                        ("Fillings", "markdown_fillings", "callback_data"),
                    ],
                    [
                        ("🔙 Back", f"help_back({prev_page_num})"),
                    ],
                ]
            )
            return await costum_cq(
                **{costum_text: text},
                reply_markup=button,
            )
        except (FloodWait, FloodPremiumWait) as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return


async def cb_help(_, callback_query):
    await callback_query.answer()
    mod_match = re.match(r"help_module\((.+?),(.+?)\)", callback_query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", callback_query.data)
    next_match = re.match(r"help_next\((.+?)\)", callback_query.data)
    back_match = re.match(r"help_back\((\d+)\)", callback_query.data)
    create_match = re.match(r"help_create", callback_query.data)
    user_id = callback_query.from_user.id
    is_bot = await dB.get_var(user_id, "is_bot")
    is_bot_pro = await dB.get_var(user_id, "is_bot_pro")
    is_bot_basic = await dB.get_var(user_id, "is_bot_basic")
    if is_bot:
        if is_bot_pro:
            visible_helpable = HELPABLE
            plan_teks = "Pro"
        elif is_bot_basic:
            visible_helpable = {
                name: data
                for name, data in HELPABLE.items()
                if not data.get("is_pro", False)
            }
            plan_teks = "Basic"
        else:
            visible_helpable = {
                name: data
                for name, data in HELPABLE.items()
                if not data.get("is_pro", False) and not data.get("is_basic", False)
            }
            plan_teks = "Lite"
    else:
        plan = await dB.get_var(user_id, "plan") or "lite"
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
    prefix = navy.get_prefix(user_id)
    x_ = next(iter(prefix))
    full = f"<a href=tg://user?id={callback_query.from_user.id}>{callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}</a>"
    cekpic = await dB.get_var(user_id, "HELP_LOGO")
    text_help = (
        await dB.get_var(user_id, "text_help")
        or f"**🤖 {BOT_NAME} by {USENAME_OWNER}**"
    )
    text_help2 = f"<blockquote>**🤖 {BOT_NAME} by {USENAME_OWNER}**</blockquote>"
    costum_cq = (
        callback_query.edit_message_caption
        if cekpic
        else callback_query.edit_message_text
    )
    costum_text = "caption" if cekpic else "text"
    if mod_match:
        module = mod_match.group(1)
        logger.info(f"line 48: {module}")
        prev_page_num = int(mod_match.group(2))
        state.set(user_id, "prev_page_num", prev_page_num)
        bot_text = f"{visible_helpable[module]['module'].__HELP__}".format(
            x_, text_help2
        )
        if "format" in bot_text:
            try:
                button_ = ikb(
                    [
                        [
                            ("Formatting", "markdown_format", "callback_data"),
                            ("Fillings", "markdown_fillings", "callback_data"),
                        ],
                        [
                            ("🔙 Back", f"help_back({prev_page_num})"),
                        ],
                    ]
                )
                return await costum_cq(
                    **{costum_text: text_markdown},
                    reply_markup=button_,
                )
            except (FloodWait, FloodPremiumWait) as e:
                return await callback_query.answer(
                    f"FloodWait {e}, Please Waiting!!", True
                )

            except MessageNotModified:
                return
        else:
            try:
                button = ikb(
                    [
                        [
                            ("🔙 Back", f"help_back({prev_page_num})", "callback_data"),
                        ]
                    ]
                )
                return await costum_cq(
                    **{costum_text: bot_text},
                    reply_markup=button,
                )
            except (FloodWait, FloodPremiumWait) as e:
                return await callback_query.answer(
                    f"FloodWait {e}, Please Waiting!!", True
                )

            except MessageNotModified:
                return

    elif prev_match:
        curr_page = int(prev_match.group(1))
        try:
            return await costum_cq(
                **{
                    costum_text: top_text.format(
                        plan_teks,
                        " ".join(prefix),
                        len(visible_helpable),
                        full,
                        text_help,
                    )
                },
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page, visible_helpable, "help", is_bot=is_bot)
                ),
            )
        except (FloodWait, FloodPremiumWait) as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return
    elif next_match:
        next_page = int(next_match.group(1))
        try:
            return await costum_cq(
                **{
                    costum_text: top_text.format(
                        plan_teks,
                        " ".join(prefix),
                        len(visible_helpable),
                        full,
                        text_help,
                    )
                },
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page, visible_helpable, "help", is_bot=is_bot)
                ),
            )
        except (FloodWait, FloodPremiumWait) as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return
    elif back_match:
        prev_page_num = int(back_match.group(1))
        try:
            return await costum_cq(
                **{
                    costum_text: top_text.format(
                        plan_teks,
                        " ".join(prefix),
                        len(visible_helpable),
                        full,
                        text_help,
                    )
                },
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        prev_page_num, visible_helpable, "help", is_bot=is_bot
                    )
                ),
            )
        except (FloodWait, FloodPremiumWait) as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return
    elif create_match:
        try:
            return await costum_cq(
                **{
                    costum_text: top_text.format(
                        plan_teks,
                        " ".join(prefix),
                        len(visible_helpable),
                        full,
                        text_help,
                    )
                },
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, visible_helpable, "help", is_bot=is_bot)
                ),
            )
        except (FloodWait, FloodPremiumWait) as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return


async def del_userbot(_, callback_query):
    user_id = callback_query.from_user.id
    if user_id not in SUDO_OWNERS:
        return await callback_query.answer(
            f"<b>GAUSAH DIPENCET YA ANJING! {callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}",
            True,
        )
    try:
        show = await bot.get_users(callback_query.data.split()[1])
        get_id = show.id
        get_mention = f"<a href=tg://user?id={get_id}>{show.first_name} {show.last_name or ''}</a>"
    except Exception:
        get_id = int(callback_query.data.split()[1])
        get_mention = f"<a href=tg://user?id={get_id}>Userbot</a>"
    for X in navy._ubot:
        if get_id == X.me.id:
            try:
                await X.unblock_user(bot.me.username)
                await bot.send_message(
                    X.me.id,
                    f"<b>💬 Masa Aktif Anda Telah Habis</b>",
                )
            except Exception:
                pass
            await dB.remove_ubot(X.me.id)
            await dB.rem_expired_date(X.me.id)
            await dB.revoke_token(X.me.id, deleted=True)
            navy._get_my_id.remove(X.me.id)
            navy._ubot.remove(X)
            await X.log_out()
            return await bot.send_message(
                LOG_SELLER,
                f"<b> ✅ {get_mention} Deleted on database</b>",
            )


async def prevnext_userbot(_, callback_query):
    await callback_query.answer()
    query = callback_query.data.split()
    count = int(query[1])
    if query[0] == "next_ub":
        if count == len(navy._ubot) - 1:
            count = 0
        else:
            count += 1
    elif query[0] == "prev_ub":
        if count == 0:
            count = len(navy._ubot) - 1
        else:
            count -= 1
    try:
        return await callback_query.edit_message_text(
            await Message.userbot(count),
            reply_markup=(ButtonUtils.userbot(navy._ubot[count].me.id, count)),
        )
    except Exception as e:
        return f"Error: {e}"


async def prevnext_userbot2(_, callback_query):
    await callback_query.answer()
    query = callback_query.data.split()
    count = int(query[1])
    if query[0] == "fakenext_ub":
        if count == len(navy._ubot) - 1:
            count = 0
        else:
            count += 1
    elif query[0] == "fakeprev_ub":
        if count == 0:
            count = len(navy._ubot) - 1
        else:
            count -= 1
    try:
        return await callback_query.edit_message_text(
            await Message.userbot(count),
            reply_markup=(ButtonUtils.fake_userbot(navy._ubot[count].me.id, count)),
        )
    except Exception as e:
        return f"Error: {e}"


async def tools_userbot(_, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    query = callback_query.data.split()
    if user_id not in SUDO_OWNERS:
        return await callback_query.answer(
            f"<b>GAUSAH REWEL YA ANJING! {callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}",
            True,
        )
    X = navy._ubot[int(query[1])]
    if query[0] == "get_otp":
        async for otp in X.search_messages(777000, limit=1):
            try:
                if not otp.text:
                    await callback_query.answer("❌ Kode tidak ditemukan", True)
                else:
                    await callback_query.edit_message_text(
                        otp.text,
                        reply_markup=(ButtonUtils.userbot(X.me.id, int(query[1]))),
                    )
                    return await X.delete_messages(X.me.id, otp.id)
            except Exception as error:
                return await callback_query.answer(error, True)
    elif query[0] == "get_phone":
        try:
            return await callback_query.edit_message_text(
                f"<b>📲 Nomer telepon <code>{X.me.id}</code> adalah <code>{X.me.phone_number}</code></b>",
                reply_markup=(ButtonUtils.userbot(X.me.id, int(query[1]))),
            )
        except Exception as error:
            return await callback_query.answer(error, True)
    elif query[0] == "get_faktor":
        code = await dB.get_var(X.me.id, "PASSWORD")
        if code == None:
            return await callback_query.answer(
                "🔐 Kode verifikasi 2 langkah tidak ditemukan", True
            )
        else:
            return await callback_query.edit_message_text(
                f"<b>🔐 Kode verifikasi 2 langkah pengguna <code>{X.me.id}</code> adalah : <code>{code}</code></b>",
                reply_markup=(ButtonUtils.userbot(X.me.id, int(query[1]))),
            )
    elif query[0] == "ub_deak":
        return await callback_query.edit_message_reply_markup(
            reply_markup=(ButtonUtils.deak(X.me.id, int(query[1])))
        )
    elif query[0] == "deak_akun":
        navy._ubot.remove(X)
        await X.invoke(raw.functions.account.DeleteAccount(reason="madarchod hu me"))
        return await callback_query.edit_message_text(
            Message.deak(X),
            reply_markup=(ButtonUtils.userbot(X.me.id, int(query[1]))),
        )


async def contact_admins(_, message):
    reply_text = (
        "<b>English:</b> Please write the message you want to convey with the hashtag #ask and please wait for the admin to reply.\n\n"
        "<b>Indonesia:</b> Silahkan tulis pesan yang ingin anda sampaikan dengan hastag #ask dan mohon tunggu sampai admin membalas."
    )
    reply_markup = ikb([[("🔙 Back", "starthome")]])
    return await message.reply(reply_text, reply_markup=reply_markup)


async def closed_user(_, callback_query):

    try:
        split = callback_query.data.split(maxsplit=1)[1]
        logger.info(f"ini split {split}")
        data = state.get(split, split)
        logger.info(f"ini data {data}")
        if not data:
            return await callback_query.answer("This button not for you fvck!!", True)
        message = next(
            (obj for obj in get_objects() if id(obj) == int(data["idm"])), None
        )
        c = message._client
        if not callback_query.from_user:
            return await callback_query.answer("ANAK ANJING!!", True)
        if callback_query.from_user.id != c.me.id:
            return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
        return await c.delete_messages(int(data["chat"]), int(data["_id"]))
    except Exception as er:
        logger.error(f"{str(er)}")


async def pm_warn(_, callback_query):
    try:
        data = callback_query.data.split()
        client = int(data[1])
        target = int(data[2])
        Flood = state.get(client, target)
        pm_warns = await dB.get_var(client, "PMLIMIT") or LIMIT
        return await callback_query.answer(
            f"⚠️ You have a chance {Flood}/{pm_warns} ❗\n\nIf you insist on sending messages continuously then you will be ⛔ blocked automatically and we will 📢 report your account as spam",
            True,
        )
    except Exception:
        logger.error(f"ERROR: {traceback.format_exc()}")


async def get_bio(_, callback_query):
    getid = int(callback_query.data.split("_")[1])
    data = state.get(getid, "bio")
    if not data:
        return await callback_query.answer("Bio not found", True)
    return await callback_query.answer(data, True)


async def copy_msg(_, callback_query):

    try:
        get_id = int(callback_query.data.split("_", 1)[1])
        message = [obj for obj in get_objects() if id(obj) == get_id][0]
        await message._client.unblock_user(bot.me.username)
        await callback_query.edit_message_text("<b>Proses Upload...</b>")
        copy = await message._client.send_message(
            bot.me.username, f"/kontol {message.text.split()[1]}"
        )
        msg = message.reply_to_message or message
        await asyncio.sleep(1.5)
        await copy.delete()
        async for get in message._client.search_messages(bot.me.username, limit=1):
            await message._client.copy_message(
                message.chat.id, bot.me.username, get.id, reply_to_message_id=msg.id
            )
            await message._client.delete_messages(
                message.chat.id, COPY_ID[message._client.me.id]
            )
            await get.delete()
    except Exception as error:
        await callback_query.edit_message_text(f"**ERROR:** <code>{error}</code>")


async def cb_notes(_, callback_query):

    data = callback_query.data.split("_")
    btn_close = state.get("close_notes", "get_note")
    dia = callback_query.from_user
    type_mapping = {
        "photo": InputMediaPhoto,
        "video": InputMediaVideo,
        "animation": InputMediaAnimation,
        "audio": InputMediaAudio,
        "document": InputMediaDocument,
    }
    try:
        notetag = data[-2].replace("cb_", "")
        gw = data[-1]
        item = [x for x in navy._ubot if int(gw) == x.me.id]
        noteval = await dB.get_var(int(gw), notetag, "notes")

        if not noteval:
            await callback_query.answer("Catatan tidak ditemukan.", True)
            return

        full = (
            f"<a href=tg://user?id={dia.id}>{dia.first_name} {dia.last_name or ''}</a>"
        )
        await dB.add_userdata(
            dia.id,
            dia.first_name,
            dia.last_name,
            dia.username,
            dia.mention,
            full,
            dia.id,
        )

        for me in item:
            tks = noteval["result"].get("text")
            note_type = noteval["type"]
            file_id = noteval.get("file_id")
            note, button = ButtonUtils.parse_msg_buttons(tks)
            teks = await Tools.escape_tag(bot, dia.id, note, Tools.parse_words)
            button = await ButtonUtils.create_inline_keyboard(button, int(gw))
            for row in btn_close.inline_keyboard:
                button.inline_keyboard.append(row)
            try:
                if note_type == "text":
                    await callback_query.edit_message_text(
                        text=teks, reply_markup=button
                    )

                elif note_type in type_mapping and file_id:
                    InputMediaType = type_mapping[note_type]
                    media = InputMediaType(media=file_id, caption=teks)
                    await callback_query.edit_message_media(
                        media=media, reply_markup=button
                    )

                else:
                    await callback_query.edit_message_caption(
                        caption=teks, reply_markup=button
                    )

            except (FloodWait, FloodPremiumWait) as e:
                return await callback_query.answer(
                    f"FloodWait {e}, Please Waiting!!", True
                )
            except MessageNotModified:
                pass

    except Exception:
        return await callback_query.answer(
            "Terjadi kesalahan saat memproses catatan.", True
        )


async def get_font(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    try:
        data = str(callback_query.data.split()[1])
        new = str(callback_query.data.split()[2])
        text = state.get(data, "FONT")
        get_new_font = gens_font(new, text)
        await callback_query.answer("Wait a minute!!", True)
        return await callback_query.edit_message_text(
            f"<b>Result:\n<code>{get_new_font}</code></b>"
        )
    except Exception as error:
        return await callback_query.answer(f"❌ Error: {error}", True)


async def prev_font(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)

    try:
        get_id = str(callback_query.data.split()[1])
        current_batch = int(callback_query.data.split()[2])
        prev_batch = current_batch - 1

        if prev_batch < 0:
            prev_batch = len(query_fonts) - 1

        keyboard = ButtonUtils.create_font_keyboard(
            query_fonts[prev_batch], get_id, prev_batch
        )

        buttons = InlineKeyboardMarkup(keyboard)
        return await callback_query.edit_message_reply_markup(reply_markup=buttons)
    except Exception as error:
        return await callback_query.answer(f"❌ Error: {error}", True)


async def next_font(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    try:
        get_id = str(callback_query.data.split()[1])
        current_batch = int(callback_query.data.split()[2])
        next_batch = current_batch + 1

        if next_batch >= len(query_fonts):
            next_batch = 0

        keyboard = ButtonUtils.create_font_keyboard(
            query_fonts[next_batch], get_id, next_batch
        )

        buttons = InlineKeyboardMarkup(keyboard)
        return await callback_query.edit_message_reply_markup(reply_markup=buttons)
    except Exception as error:
        return await callback_query.answer(f"❌ Error: {error}", True)


async def refresh_cat(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    uniq = str(callback_query.data.split("_")[2])
    await callback_query.answer("Please wait a minute", True)
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
            await callback_query.edit_message_animation(
                cat_url,
                caption="<blockquote><b>Meow 😽</b></blockquote>",
                reply_markup=buttons,
            )
        else:
            await callback_query.edit_message_media(
                InputMediaPhoto(
                    media=cat_url, caption="<blockquote><b>Meow 😽</b></blockquote>"
                ),
                reply_markup=buttons,
            )
    else:
        await callback_query.edit_message_text("Failed to refresh cat picture 🙀")


async def bola_date(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)

    split = callback_query.data.split()
    if len(split) > 1:
        state_key = split[1]
        stored_data = state.get(state_key, state_key)

        buttons = []
        temp_row = []
        for liga_date in stored_data:
            button = Ikb(
                text=liga_date["LigaDate"],
                callback_data=f"bola_matches {state_key} {liga_date['LigaDate']}",
            )
            temp_row.append(button)

            if len(temp_row) == 3:
                buttons.append(temp_row)
                temp_row = []

        if temp_row:
            buttons.append(temp_row)

        buttons.append(
            [Ikb(text="Close", callback_data=f"close inline_bola {state_key}")]
        )
        keyboard = InlineKeyboardMarkup(buttons)

        return await callback_query.edit_message_text(
            text="<b>Select a date to view football matches:</b>",
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    else:
        return await callback_query.edit_message_text("No data found.")


async def bola_matches(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    split = callback_query.data.split()
    if len(split) > 2:
        state_key = split[1]
        selected_date = split[2]
        stored_data = state.get(state_key, "jadwal_bola")

        date_matches = next(
            (
                date
                for date in stored_data
                if date["LigaDate"].split()[0] == selected_date.split()[0]
            ),
            None,
        )

        if date_matches:
            text = f"Football Matches on {selected_date}\n\n"
            for league in date_matches["LigaItem"]:
                text += f"🏆 {league['NameLiga']}\n"
                for match in league["Match"]:
                    text += f"⚽ {match['team']} at {match['time']}\n"

            buttons = [
                [Ikb(text="« Back", callback_data=f"bola_date {state_key}")],
                [Ikb(text="Close", callback_data=f"close inline_bola {state_key}")],
            ]
            keyboard = InlineKeyboardMarkup(buttons)

            return await callback_query.edit_message_text(
                text=f"<blockquote><b>{text}</b></blockquote>",
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
        else:
            return await callback_query.answer("Silahkan ulangi fitur bola!!", True)


async def rest_anime(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    data = callback_query.data.split("_")
    page = int(data[1])
    uniq = str(data[2])
    berita = state.get(uniq, "anime")
    berita = berita["anime"]
    if not berita:
        await callback_query.answer("Halaman tidak ditemukan.", show_alert=True)
        return
    total_photos = len(berita)
    if page < 0 or page >= total_photos:
        await callback_query.answer("Halaman tidak ditemukan.", show_alert=True)
        return
    buttons = []
    nav_buttons = []
    if page > 0:
        nav_buttons.append(Ikb("⬅️ Prev", callback_data=f"restanime_{page - 1}_{uniq}"))
    if page < total_photos - 1:
        nav_buttons.append(Ikb("➡️ Next", callback_data=f"restanime_{page + 1}_{uniq}"))
    if nav_buttons:
        buttons.append(nav_buttons)
    buttons.append([Ikb("❌ Close", callback_data=f"close inline_anime {uniq}")])
    title = berita[page].get("title", "-")
    thumb = berita[page].get("thumbnail", "-")
    episode = berita[page].get("episode", "-")
    release = berita[page].get("release", "-")
    link = berita[page].get("link", "-")
    caption = f"""
**Title:** `{title}`
**Episode:** {episode}
**Release:** {release}
**Link:** <a href='{link}'>Here</a>
"""
    reply_markup = InlineKeyboardMarkup(buttons)
    return await callback_query.edit_message_media(
        media=InputMediaPhoto(media=thumb, caption=caption),
        reply_markup=reply_markup,
    )


async def rest_donghua(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    data = callback_query.data.split("_")
    page = int(data[1])
    uniq = str(data[2])
    berita = state.get(uniq, "donghua")
    if not berita:
        await callback_query.answer("Halaman tidak ditemukan.", show_alert=True)
        return
    total_photos = len(berita)
    if page < 0 or page >= total_photos:
        await callback_query.answer("Halaman tidak ditemukan.", show_alert=True)
        return
    buttons = []
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            Ikb("⬅️ Prev", callback_data=f"restdonghua_{page - 1}_{uniq}")
        )
    if page < total_photos - 1:
        nav_buttons.append(
            Ikb("➡️ Next", callback_data=f"restdonghua_{page + 1}_{uniq}")
        )
    if nav_buttons:
        buttons.append(nav_buttons)
    buttons.append([Ikb("❌ Close", callback_data=f"close inline_donghua {uniq}")])
    title = berita[page].get("title")
    episode = berita[page].get("episode")
    url = berita[page].get("url")
    judul = f"**Title:** {title}\n**Episode:** {episode}\n**Link:** {url}\n"
    thumb = berita[page].get("cover")
    reply_markup = InlineKeyboardMarkup(buttons)
    return await callback_query.edit_message_media(
        media=InputMediaPhoto(media=thumb, caption=judul),
        reply_markup=reply_markup,
    )


async def rest_comic(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    data = callback_query.data.split("_")
    page = int(data[1])
    uniq = str(data[2])
    berita = state.get(uniq, "comic")
    if not berita:
        await callback_query.answer("Halaman tidak ditemukan.", show_alert=True)
        return
    total_photos = len(berita)
    if page < 0 or page >= total_photos:
        await callback_query.answer("Halaman tidak ditemukan.", show_alert=True)
        return
    buttons = []
    nav_buttons = []
    if page > 0:
        nav_buttons.append(Ikb("⬅️ Prev", callback_data=f"restcomic_{page - 1}_{uniq}"))
    if page < total_photos - 1:
        nav_buttons.append(Ikb("➡️ Next", callback_data=f"restcomic_{page + 1}_{uniq}"))
    if nav_buttons:
        buttons.append(nav_buttons)
    buttons.append([Ikb("❌ Close", callback_data=f"close inline_comic {uniq}")])
    title = berita[page].get("title")
    chapter = berita[page].get("chapters", [{}])[0]
    episode = chapter.get("title", "-")
    date = chapter.get("date", "-")
    chapter_url = chapter.get("url", "")
    if "https://komiku.id" in chapter_url and not chapter_url.startswith(
        "https://komiku.id/"
    ):
        chapter_url = chapter_url.replace("https://komiku.id", "https://komiku.id/")
    judul = f"**Title:** {title}\n**Chapters:** {episode}\n**Link:** {chapter_url}\n**Uploaded:** {date}"
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.edit_message_text(judul, reply_markup=reply_markup)


async def news_(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    data = callback_query.data.split("_")
    page = int(data[1])
    uniq = str(data[2])
    berita = state.get(uniq, "news")
    if not berita:
        await callback_query.answer(
            "Tidak ada berita untuk ditampilkan.", show_alert=True
        )
        return
    total_photos = len(berita)
    if page < 0 or page >= total_photos:
        await callback_query.answer("Halaman tidak ditemukan.", show_alert=True)
        return
    buttons = []
    nav_buttons = []
    buttons.append([Ikb("📮 Link", url=f"{berita[page]['link']}")])
    if page > 0:
        nav_buttons.append(Ikb("⬅️ Prev", callback_data=f"news_{page - 1}_{uniq}"))
    if page < total_photos - 1:
        nav_buttons.append(Ikb("➡️ Next", callback_data=f"news_{page + 1}_{uniq}"))
    if nav_buttons:
        buttons.append(nav_buttons)
    buttons.append([Ikb("❌ Close", callback_data=f"close inline_news {uniq}")])
    title = berita[page]["title"]
    date = berita[page].get("time", "-")
    thumb = berita[page]["image_thumbnail"]
    content = berita[page]["content"]
    clean_content = content[:500]
    judul = f"""
<blockquote expandable>
**Title:** {title}
**Uploaded:** {date}
**Content:** {clean_content}
</blockquote>
"""
    reply_markup = InlineKeyboardMarkup(buttons)
    return await callback_query.edit_message_media(
        media=InputMediaPhoto(media=thumb, caption=judul),
        reply_markup=reply_markup,
    )


async def chatai_with_chatgpt_normal(_, query, uniq):
    data = state.get(uniq, "chatai")
    prompt = data["prompt"]
    get_id = data["idm"]
    message = [obj for obj in get_objects() if id(obj) == get_id][0]
    message.from_user.id
    chat_id = message.chat.id
    ids = (unpack_inline_message_id(query.inline_message_id)).id
    try:
        await message._client.delete_messages(
            message.chat.id,
            ids,
        )
    except Exception:
        pass
    data_json = [
        {
            "role": "system",
            "content": "Kamu adalah asisten paling canggih yang berbahasa Indonesia gaul, dan jangan gunakan bahasa inggris sebelum saya memulai duluan.",
        },
        {"role": "user", "content": prompt},
    ]
    while True:
        try:
            url = "https://api.siputzx.my.id/api/ai/gpt3"
            r = await Tools.fetch.post(url, json=data_json)
            if r.status_code == 200:
                result = r.json().get("data")
                if len(result) > 4096:
                    with open(f"{prompt.split()[1]}.txt", "wb") as file:
                        file.write(result.encode("utf-8"))
                    reply = await message._client.send_document(
                        chat_id, f"{prompt.split()[1]}.txt"
                    )
                    next_message = await message._client.ask(
                        chat_id,
                        f"<b><u>Chat with ChatGpt</u></b>\nQuestion:</b>\n<blockquote>{prompt}</blockquote>\n\n**Type `stopped ask` to end the conversation.**",
                        reply_to_message_id=reply.id,
                        timeout=300,
                    )
                else:
                    if len(result) > 496:
                        caption = f"<blockquote expandable>{result}</blockquote>"
                    else:
                        caption = f"<blockquote>{result}</blockquote>"
                    next_message = await message._client.ask(
                        chat_id,
                        f"<b><u>Chat with ChatGpt</u></b>\n<b>Question:\n<blockquote>{prompt}</blockquote>\n\nAnswer:\n</b>{caption}\n\n**Type `stopped ask` to end the conversation.**",
                    )
                    if next_message.text.lower() == "stopped ask":
                        await next_message.reply(f"**Conversation ended.**")
                        break
                    prompt = next_message.text
            else:
                return await message.reply("<b>Please try again later..</b>")
        except Exception:
            logger.error(traceback.format_exc())
            return await message.reply("<b>Please try again later..</b>")


async def chat_gpt(client, query):
    if not query.from_user:
        return await query.answer("ANAK ANJING!!", True)
    if query.from_user.id not in navy._get_my_id:
        return await query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    mode = str(query.data.split("_")[1])
    uniq = str(query.data.split("_")[2])
    data = state.get(uniq, "chatai")
    if not data:
        return await query.answer(
            "Data not found, please create new conversation.", True
        )
    if mode == "normal":
        return await chatai_with_chatgpt_normal(client, query, uniq)
    elif mode == "audio":
        msg = "<b>Please select model voice first.</b>"
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
                Ikb(model.capitalize(), callback_data=f"gptvoice_{model}_{uniq}")
            )
            if idx % 3 == 0:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        reply_markup = InlineKeyboardMarkup(buttons)
        return await query.edit_message_text(msg, reply_markup=reply_markup)


async def gpt_voice(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    data = callback_query.data.split("_")
    args = str(data[1])
    uniq = str(data[2])
    query = state.get(uniq, "chatai")
    if not query:
        return await callback_query.answer(
            "Data telah usang. Silahkan jalankan ulang fitur nya.", True
        )
    prompt = query["prompt"]
    get_id = query["idm"]
    message = [obj for obj in get_objects() if id(obj) == get_id][0]
    chat_id = message.chat.id
    user_id = message.from_user.id
    ids = (unpack_inline_message_id(callback_query.inline_message_id)).id
    try:
        await message._client.delete_messages(
            message.chat.id,
            ids,
        )
    except Exception:
        pass
    if user_id not in CONVERSATIONS:
        CONVERSATIONS[user_id] = []
    while True:
        try:
            headers = {"mg-apikey": API_MAELYN}
            params = {"q": prompt, "model": args}
            url = "https://api.maelyn.sbs/api/chatgpt/audio"
            response = await Tools.fetch.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()["result"]
                audio = data.get("url")
                CONVERSATIONS[user_id].append(audio)
                reply = await message._client.send_audio(chat_id, audio)
                next_message = await message._client.ask(
                    chat_id,
                    f"**Model: {args}**\n\n<b>Question:\n<blockquote>{prompt}</blockquote>\n\n**Type `stopped ask` to end the conversation.**",
                    reply_to_message_id=reply.id,
                )
                if next_message.text.lower() == "stopped ask":
                    del CONVERSATIONS[user_id]
                    await next_message.reply(f"**Conversation ended.**")
                    break
                prompt = next_message.text
            else:
                return await message.reply("<b>Please try again later..</b>")
        except Exception:
            logger.error(traceback.format_exc())
            return await message.reply("<b>Please try again later..</b>")


async def cine_plax(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    data = callback_query.data.split("_")
    uniq = str(data[2])
    page = int(data[1])
    type_ = state.get(uniq, "cineplax")
    movies = state.get(uniq, "data_cineplax", [])
    if page * 5 >= len(movies):
        await callback_query.answer("Tidak ada halaman berikutnya.", show_alert=True)
        return

    buttons = []
    for movie in movies[page * 5 : (page + 1) * 5]:
        rating = movie.get("label", "-").split("/")[-1].replace(".png", "")
        if type_ == "soon":
            link = movie["link"].replace("https://21cineplex.com/comingsoon", "", 1)
        else:
            link = movie["link"].replace("https://21cineplex.com/", "", 1)
    if page > 0:
        buttons.append([Ikb("📮 Link", url=link)])
        buttons.append(
            [
                Ikb("⬅️ Prev", callback_data=f"cineplax_{page - 1}_{uniq}"),
                Ikb("➡️ Next", callback_data=f"cineplax_{page + 1}_{uniq}"),
            ]
        )
    buttons.append([Ikb("❌ Close", callback_data=f"close inline_cineplax {uniq}")])
    reply_markup = InlineKeyboardMarkup(buttons)

    caption = f"""
<blockquote>🎬 **Title: {movie['title']}**

**Rating:** {rating}</blockquote>
"""
    await callback_query.edit_message_media(
        media=InputMediaPhoto(
            media=movie["poster"],
            caption=caption,
        ),
        reply_markup=reply_markup,
    )


async def cek_expired_cb(_, cq):
    user_id = int(cq.data.split()[1])
    try:
        expired = await dB.get_expired_date(user_id)
        habis = expired.astimezone(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M")
        return await cq.answer(f"⏳ Waktu: {habis}", True)
    except Exception:
        return await cq.answer("✅ Sudah tidak aktif", True)


async def closed_bot(_, cq):
    await cq.answer()
    if await dB.get_var(cq.from_user.id, "is_bot"):
        await dB.remove_var(cq.from_user.id, "is_bot")
        await dB.remove_var(cq.from_user.id, "is_bot_pro")
    try:
        return await cq.message.delete()
    except Exception:
        return


async def nxt_spotify(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    data = callback_query.data.split("_")
    await callback_query.answer("Please wait a minute", True)

    page = int(data[1])
    uniq = str(data[2])

    audios = state.get(uniq, uniq)
    per_page = 5
    total_pages = (len(audios) + per_page - 1) // per_page

    if audios is None or page >= total_pages:
        return await callback_query.answer(
            "Tidak ada halaman berikutnya.", show_alert=True
        )

    sliced = audios[page * per_page : (page + 1) * per_page]
    caption = f"<blockquote expandable><b>🎧 Spotify Results (Page {page+1})</b>\n\n"
    buttons = []

    for idx, audio in enumerate(sliced):
        caption += f"""
<b>{idx + 1}. {audio['title']}</b>
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
    nav_buttons = [(str(i + 1), f"nxtspotify_{i}_{uniq}") for i in range(total_pages)]
    buttons.append(nav_buttons)
    buttons.append([("❌ Close", f"close inline_spotify {uniq}")])

    return await callback_query.edit_message_text(
        caption,
        reply_markup=ikb(buttons),
        disable_web_page_preview=True,
    )


async def dl_spot(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    await callback_query.answer("Please wait a minute", True)
    try:
        data = callback_query.data.split("_")
        uniq = str(data[1])
        index = int(data[2])
        audios = state.get(uniq, uniq)

        if not audios or index >= len(audios):
            return await callback_query.answer("Track not found!", show_alert=True)

        audio = audios[index]
        get_id = state.get(uniq, "idm_spotdl")
        message = [obj for obj in get_objects() if id(obj) == get_id][0]
        client = message._client
        em = Emoji(client)
        await em.get()

        now = time.time()
        proses = await message.reply(f"{em.proses}**Get detail information...**")

        link = audio["track_url"]
        url = await Spotify.track(link)

        (
            file_path,
            info,
            title,
            duration,
            views,
            channel,
            url,
            _,
            thumb,
            data_ytp,
        ) = await youtube.download(url.get("file_path"), as_video=False)

        thumbnail = wget.download(thumb)
        caption = data_ytp.format(
            info,
            title,
            Tools.seconds_to_min(int(duration)),
            views,
            channel,
            url,
            client.me.mention,
        )

        ids = (unpack_inline_message_id(callback_query.inline_message_id)).id
        try:
            await client.delete_messages(message.chat.id, ids)
        except Exception:
            pass

        await message.reply_audio(
            audio=file_path,
            title=title,
            thumb=thumbnail,
            performer=channel,
            duration=duration,
            caption=caption,
            progress=youtube.progress,
            progress_args=(proses, now, f"<b>Sending request...</b>", title),
        )
        return await proses.delete()

    except Exception:
        logger.error(f"Eror download spotify: {traceback.format_exc()}")


async def viewchord(_, callback):
    if not callback.from_user:
        return await callback.answer("ANAK ANJING!!", True)
    if callback.from_user.id not in navy._get_my_id:
        return await callback.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    try:
        parts = callback.data.split("_", 2)
        if len(parts) != 3:
            return await callback.answer("❌ Callback tidak valid.", show_alert=True)

        _, index_str, uniq = parts
        index = int(index_str)

        data = state.get(uniq, "chord") or []
        if index < 0 or index >= len(data):
            return await callback.answer("❌ Data tidak ditemukan.", show_alert=True)

        song = data[index]
        text = f"""
<blockquote expandable>
<b>🎵 {song['title']}</b>
🎤 {song['artist']}
🔗 <a href=\"{song['link']}\">Open Chord</a>

<code>{song["detail"][:4000]}</code>
</blockquote>
"""

        nav_buttons = [
            ("🎵 {}".format(i + 1), f"viewchord_{i}_{uniq}") for i in range(len(data))
        ]
        nav_layout = [nav_buttons[i : i + 5] for i in range(0, len(nav_buttons), 5)]
        nav_layout.append([("❌ Close", f"close inline_chord {uniq}")])

        await callback.edit_message_text(
            text, reply_markup=ikb(nav_layout), disable_web_page_preview=True
        )
    except MessageNotModified:
        await callback.answer("❌ LU PEA", show_alert=True)
    except Exception:
        await callback.answer("⚠️ Terjadi kesalahan.", show_alert=True)
        print(traceback.format_exc())


async def an1cb(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    data = callback_query.data.split("_")
    page = int(data[1])
    uniq = str(data[2])
    result = state.get(uniq, uniq)
    if not result:
        await callback_query.answer(
            "Tidak ada halaman untuk ditampilkan.", show_alert=True
        )
        return
    total_result = len(result)
    if page < 0 or page >= total_result:
        await callback_query.answer("Halaman tidak ditemukan.", show_alert=True)
        return
    title = result[page].get("title")
    link = result[page].get("link")
    thumbnail = result[page].get("image")
    type = result[page].get("type")
    developer = result[page].get("developer")
    rating = result[page]["rating"]
    msg = f"""
**Title:** {title}
**Developer:** {developer}
**Rating:** {rating.get('value', '-')} | {rating.get('percentage', '-')}%
**Type:** {type}
"""
    buttons = []
    nav_buttons = []
    buttons.append([Ikb("📮 Link", url=link)])
    if page > 0:
        nav_buttons.append(Ikb("⬅️ Prev", callback_data=f"apkinfocb_{page - 1}_{uniq}"))
    if page < total_result - 1:
        nav_buttons.append(Ikb("➡️ Next", callback_data=f"apkinfocb_{page + 1}_{uniq}"))
    if nav_buttons:
        buttons.append(nav_buttons)
    buttons.append([Ikb("❌ Close", callback_data=f"close inline_apkan1 {uniq}")])
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.edit_message_media(
        media=InputMediaPhoto(media=thumbnail, caption=msg), reply_markup=reply_markup
    )


async def moddycb(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    data = callback_query.data.split("_")
    page = int(data[1])
    uniq = str(data[2])
    result = state.get(uniq, uniq)
    if not result:
        await callback_query.answer(
            "Tidak ada halaman untuk ditampilkan.", show_alert=True
        )
        return
    total_result = len(result)
    if page < 0 or page >= total_result:
        await callback_query.answer("Halaman tidak ditemukan.", show_alert=True)
        return
    title = result[page].get("title")
    link = result[page].get("link")
    thumbnail = result[page].get("icon")
    genre = result[page].get("genre")
    rating = result[page]["rating"]
    msg = f"""
**Title:** {title}
**Rating:** {rating.get('value', '-')} | {rating.get('percentage', '-')}%
**Genre:** {genre}
"""
    buttons = []
    nav_buttons = []
    buttons.append([Ikb("📮 Link", url=link)])
    if page > 0:
        nav_buttons.append(Ikb("⬅️ Prev", callback_data=f"moddycb_{page - 1}_{uniq}"))
    if page < total_result - 1:
        nav_buttons.append(Ikb("➡️ Next", callback_data=f"moddycb_{page + 1}_{uniq}"))
    if nav_buttons:
        buttons.append(nav_buttons)
    buttons.append([Ikb("❌ Close", callback_data=f"close inline_apkmoddy {uniq}")])
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.edit_message_media(
        media=InputMediaPhoto(media=thumbnail, caption=msg), reply_markup=reply_markup
    )


async def viewgempa(_, callback):
    if not callback.from_user:
        return await callback.answer("ANAK ANJING!!", True)
    if callback.from_user.id not in navy._get_my_id:
        return await callback.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    _, page, uniq = callback.data.split("_")
    page = int(page)

    data_result = state.get(uniq, uniq)
    if not data_result:
        return await callback.answer("Data tidak ditemukan!", show_alert=True)

    gempa_list = data_result.get("terkini", {}).get("Infogempa", {}).get("gempa", [])
    if not gempa_list:
        return await callback.answer("Data kosong!", show_alert=True)

    per_page = 5
    start = page * per_page
    end = start + per_page
    sliced = gempa_list[start:end]

    buttons = []
    for idx, item in enumerate(sliced):
        judul = f"{item['Tanggal']} {item['Magnitude']} M - {item['Wilayah'][:20]}"
        callback_data = f"nxtbmkg_{uniq}_{start + idx}"
        buttons.append([("⬇️ " + judul, callback_data)])

    total_pages = (len(gempa_list) + per_page - 1) // per_page
    nav_buttons = [(str(i + 1), f"viewgempa_{i}_{uniq}") for i in range(total_pages)]
    buttons.append(nav_buttons)

    await callback.edit_message_text(
        f"📊 Menampilkan daftar gempa ke {start + 1}–{min(end, len(gempa_list))} dari {len(gempa_list)} total.",
        reply_markup=ikb(buttons),
    )


async def nxtbmkg(_, callback):
    if not callback.from_user:
        return await callback.answer("ANAK ANJING!!", True)
    if callback.from_user.id not in navy._get_my_id:
        return await callback.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    _, uniq, idx = callback.data.split("_")
    idx = int(idx)

    data_result = state.get(uniq, uniq)
    if not data_result:
        return await callback.answer("Data tidak ditemukan!", show_alert=True)

    gempa_list = data_result.get("terkini", {}).get("Infogempa", {}).get("gempa", [])
    if idx >= len(gempa_list):
        return await callback.answer("Indeks gempa tidak valid!", show_alert=True)

    gempa = gempa_list[idx]

    msg = f"""
<blockquote expandable>
<b>📍 Lokasi:</b> <code>{gempa.get('Wilayah')}</code>
📅 <b>Tanggal:</b> <code>{gempa.get('Tanggal')}</code>
🕒 <b>Jam:</b> <code>{gempa.get('Jam')}</code>
💥 <b>Magnitudo:</b> <code>{gempa.get('Magnitude')}</code>
📏 <b>Kedalaman:</b> <code>{gempa.get('Kedalaman')}</code>
📌 <b>Koordinat:</b> <code>{gempa.get('Coordinates')}</code>
🌊 <b>Potensi:</b> <code>{gempa.get('Potensi')}</code>
😵 <b>Dirasakan:</b> <code>{gempa.get('Dirasakan')}</code>

<i>Sumber: BMKG</i>
</blockquote>
"""
    per_page = 5
    start = idx * per_page
    end = start + per_page
    sliced = gempa_list[start:end]

    buttons = []
    for idx, item in enumerate(sliced):
        judul = f"{item['Tanggal']} {item['Magnitude']} M - {item['Wilayah'][:20]}"
        callback_data = f"nxtbmkg_{uniq}_{start + idx}"
        buttons.append([("⬇️ " + judul, callback_data)])

    total_pages = (len(gempa_list) + per_page - 1) // per_page
    nav_buttons = [(str(i + 1), f"viewgempa_{i}_{uniq}") for i in range(total_pages)]
    buttons.append(nav_buttons)
    try:
        await callback.edit_message_text(msg, reply_markup=ikb(buttons))
    except MessageNotModified:
        await callback.answer("⛔ Sudah di halaman ini", show_alert=True)
    except Exception:
        await callback.answer("⚠️ Terjadi kesalahan.", show_alert=True)
        print(traceback.format_exc())


async def nxt_ytsearch(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    data = callback_query.data.split("_")
    await callback_query.answer("Please wait a minute", True)
    page = int(data[1])
    uniq = str(data[2])
    audios = state.get(uniq, uniq)
    per_page = 5
    total_pages = (len(audios) + per_page - 1) // per_page

    if audios is None or page >= total_pages:
        return await callback_query.answer(
            "Tidak ada halaman berikutnya.", show_alert=True
        )

    sliced = audios[page * per_page : (page + 1) * per_page]
    caption = f"<blockquote expandable><b>🎧 Youtube Results (Page {page+1})</b>\n"
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
    nav_buttons = [(str(i + 1), f"nxtytsearch_{i}_{uniq}") for i in range(total_pages)]
    buttons.append(nav_buttons)
    buttons.append([("❌ Close", f"close inline_youtube {uniq}")])

    return await callback_query.edit_message_text(
        caption,
        reply_markup=ikb(buttons),
        disable_web_page_preview=True,
    )


async def dl_ytsearch(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    await callback_query.answer("Please wait...", True)
    try:
        data = callback_query.data.split("_")
        uniq = str(data[1])
        index = int(data[2])
        is_video = state.get(uniq, "as_video")
        audios = state.get(uniq, uniq)

        if not audios or index >= len(audios):
            return await callback_query.answer("Track not found!", show_alert=True)

        audio = audios[index]
        get_id = state.get(uniq, "idm_ytsearch")
        message = [obj for obj in get_objects() if id(obj) == get_id][0]
        client = message._client
        em = Emoji(client)
        await em.get()

        now = time.time()
        proses = await message.reply(f"{em.proses}**Get detail information...**")

        link = audio["url"]
        (
            file_path,
            info,
            title,
            duration,
            views,
            channel,
            url,
            _,
            thumb,
            data_ytp,
        ) = await youtube.download(link, as_video=is_video)

        thumbnail = wget.download(thumb)
        caption = data_ytp.format(
            info,
            title,
            Tools.seconds_to_min(int(duration)),
            views,
            channel,
            url,
            client.me.mention,
        )

        ids = (unpack_inline_message_id(callback_query.inline_message_id)).id
        try:
            await client.delete_messages(message.chat.id, ids)
        except Exception:
            pass
        if is_video:
            await client.send_video(
                message.chat.id,
                video=file_path,
                thumb=thumbnail,
                file_name=title,
                duration=duration,
                supports_streaming=True,
                caption=caption,
                progress=youtube.progress,
                progress_args=(
                    proses,
                    now,
                    f"{em.proses}<b>Trying to upload...</b>",
                    title,
                ),
                reply_to_message_id=message.id,
            )
        else:
            await client.send_audio(
                message.chat.id,
                audio=file_path,
                thumb=thumbnail,
                file_name=title,
                performer=channel,
                duration=duration,
                caption=caption,
                progress=youtube.progress,
                progress_args=(
                    proses,
                    now,
                    f"{em.proses}<b>Trying to upload...</b>",
                    title,
                ),
                reply_to_message_id=message.id,
            )
        return await proses.delete()

    except Exception:
        logger.error(f"Eror download youtube: {traceback.format_exc()}")


async def selected_topic(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    data = callback_query.data.split("_")
    chat_id = int(data[1])
    tread_id = int(data[2])
    title = str(data[3])
    await dB.set_var(chat_id, "SELECTED_TOPIC", tread_id)
    return await callback_query.answer(f"Changed send topic to {title}.")
