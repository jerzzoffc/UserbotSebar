import asyncio
import importlib
import traceback
from datetime import datetime

import hydrogram
from dateutil.relativedelta import relativedelta
from pyrogram.helpers import ikb
from pyrogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                            ReplyKeyboardRemove)
from pytz import timezone

from clients import UserBot, bot, navy
from config import (AKSES_DEPLOY, API_HASH, API_ID, BOT_ID, LOG_SELLER,
                    MAX_BOT, SUDO_OWNERS, WAJIB_JOIN)
from database import dB
from helpers import ButtonUtils, Message
from logs import logger
from plugins import _PLUGINS


async def setExpiredUser(user_id):
    if user_id in SUDO_OWNERS:
        now = datetime.now(timezone("Asia/Jakarta"))
        expired = now + relativedelta(months=12)
        await dB.set_expired_date(user_id, expired)
    else:
        now = datetime.now(timezone("Asia/Jakarta"))
        expired = now + relativedelta(months=1)
        await dB.set_expired_date(user_id, expired)


async def mari_buat_userbot(client, message):
    user_id = message.from_user.id
    if len(navy._ubot) == MAX_BOT:
        buttons = ikb(
            [[("💬 Hubungi Admins", "calladmins")], [("🔙 Back", "starthome")]]
        )
        return await message.reply(
            f"""
<b>❌ Tidak dapat membuat Userbot !</b>

<b>📚 Karena Telah Mencapai Yang Telah Di Tentukan : {len(navy._ubot)}</b>

<b>👮‍♂ Silakan Hubungi Admins . </b>
""",
            reply_markup=buttons,
        )
    get_exp_user = await dB.get_expired_date(user_id)
    now = datetime.now(timezone("Asia/Jakarta"))
    if get_exp_user and now >= get_exp_user:
        await message.reply(
            f"**Masa aktif kamu `{get_exp_user.astimezone(timezone('Asia/Jakarta')).strftime('%Y-%m-%d %H:%M')}` sudah melebihi batas waktu yang ditentukan, jadi kamu tidak bisa memasang userbot lagi\n\nSilahkan lakukan pembayaran lagi untuk pemasangan userbot!!**",
            reply_markup=ikb([[("🔙 Back", "starthome")]]),
        )
        return await dB.rem_expired_date(user_id)
    if not get_exp_user and user_id not in AKSES_DEPLOY:
        buttons = ikb(
            [
                [("📃 Saya Setuju", "go_payment")],
                [("🔙 Back", "starthome"), ("❌ Tutup", "buttonclose")],
            ]
        )
        text = f"<blockquote expandable>{await Message.policy_message()}</blockquote>"
        return await message.reply(
            text,
            disable_web_page_preview=True,
            reply_markup=buttons,
        )
    else:
        return await create_userbots(client, message)


async def create_userbots(client, message):
    try:
        user_id = message.from_user.id
        anu = ReplyKeyboardMarkup(
            [
                [KeyboardButton(text="Kontak Saya", request_contact=True)],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        try:
            phone = await client.ask(
                user_id,
                f"<blockquote><b>Silahkan klik tombol <u>Kontak Saya</u> untuk mengirimkan Nomor Telepon Telegram Anda.</b></blockquote>",
                reply_markup=anu,
            )
            phone_number = phone.contact.phone_number
        except AttributeError:
            try:
                phone = await client.ask(
                    user_id,
                    f"<blockquote><b>Silahkan klik tombol <u>Kontak Saya</u> untuk mengirimkan Nomor Telepon Telegram Anda.</b></blockquote>",
                    reply_markup=anu,
                )
                phone_number = phone.contact.phone_number
            except Exception:
                return await bot.send_message(
                    user_id,
                    "<blockquote><b>PEA, punya mata dipake buat baca!! jangan BOKEP mulu.</b></blockquote>",
                    reply_markup=ButtonUtils.start_menu(is_admin=False),
                )
        new_client = hydrogram.Client(
            name=str(user_id),
            api_id=API_ID,
            api_hash=API_HASH,
            in_memory=True,
        )
        await asyncio.sleep(2)
        get_otp = await client.send_message(
            user_id,
            f"<b><blockquote>Sedang Mengirim Kode OTP...</blockquote></b>",
            reply_markup=ReplyKeyboardRemove(),
        )
        await new_client.connect()
        try:
            code = await new_client.send_code(phone_number.strip())
        except hydrogram.errors.exceptions.bad_request_400.ApiIdInvalid as AID:
            await get_otp.delete()
            return await client.send_message(user_id, AID)
        except hydrogram.errors.exceptions.bad_request_400.PhoneNumberInvalid as PNI:
            await get_otp.delete()
            return await client.send_message(user_id, PNI)
        except hydrogram.errors.exceptions.bad_request_400.PhoneNumberFlood as PNF:
            await get_otp.delete()
            return await client.send_message(user_id, PNF)
        except hydrogram.errors.exceptions.bad_request_400.PhoneNumberBanned as PNB:
            await get_otp.delete()
            return await client.send_message(user_id, PNB)
        except hydrogram.errors.exceptions.bad_request_400.PhoneNumberUnoccupied as PNU:
            await get_otp.delete()
            return await client.send_message(user_id, PNU)
        except Exception as error:
            await get_otp.delete()
            return await client.send_message(
                user_id,
                f"<b>ERROR:</b> {error}",
                reply_markup=ButtonUtils.start_menu(is_admin=False),
            )
        await get_otp.delete()
        while True:
            otp = await client.ask(
                user_id,
                f"<b><blockquote>Silakan Periksa Kode OTP dari <a href=tg://openmessage?user_id=777000>Akun Telegram</a> Resmi. Kirim Kode OTP ke sini setelah membaca Format di bawah ini.</b>\n\nJika Kode OTP adalah <code>12345</code> Tolong <b>[ TAMBAHKAN SPASI ]</b> kirimkan Seperti ini <code>1 2 3 4 5</code>.</blockquote></b>",
            )
            if otp.text.startswith("/"):
                return await client.send_message(
                    user_id,
                    f"<blockquote><b>Proses di batalkan.</b></blockquote>",
                    reply_markup=ButtonUtils.start_menu(is_admin=False),
                )
            otp_code = otp.text
            try:
                await new_client.sign_in(
                    phone_number.strip(),
                    code.phone_code_hash,
                    phone_code=" ".join(str(otp_code)),
                )
                break
            except hydrogram.errors.exceptions.bad_request_400.PhoneCodeInvalid:
                await client.send_message(
                    user_id, "<b>❌ Kode OTP salah. Coba lagi.</b>"
                )
                continue
            except hydrogram.errors.exceptions.bad_request_400.PhoneCodeExpired:
                return await client.send_message(
                    user_id, "<b>❌ Kode OTP Expired. Silahkan ulangi proses.</b>"
                )
            except hydrogram.errors.exceptions.bad_request_400.BadRequest as error:
                return await client.send_message(
                    user_id,
                    f"<b>ERROR:</b> {error}",
                    reply_markup=ButtonUtils.start_menu(is_admin=False),
                )
            except hydrogram.errors.exceptions.unauthorized_401.SessionPasswordNeeded:
                two_step_code = await client.ask(
                    user_id,
                    f"<b><blockquote>Akun anda Telah mengaktifkan Verifikasi Dua Langkah. Silahkan Kirimkan Passwordnya.</blockquote></b>",
                )
                if two_step_code.text.startswith("/"):
                    return await client.send_message(
                        user_id,
                        f"<blockquote><b>Proses di batalkan.</b></blockquote>",
                        reply_markup=ButtonUtils.start_menu(is_admin=False),
                    )
                new_code = two_step_code.text
                try:
                    await new_client.check_password(new_code)
                    await dB.set_var(user_id, "PASSWORD", new_code)
                except Exception as error:
                    await client.send_message(
                        user_id,
                        "<b>❌ V2L yang anda masukkan salah!!. Silahkan masukkan dengan benar.</b>",
                    )
                    continue
            break
        session_string = await new_client.export_session_string()
        await new_client.disconnect()
        new_client.storage.session_string = session_string
        new_client.in_memory = False
        bot_msg = await client.send_message(
            user_id,
            f"<b><blockquote>Tunggu proses selama 1-5 menit...\nKami sedang menghidupkan Userbot Anda.</blockquote></b>",
            disable_web_page_preview=True,
        )
        await asyncio.sleep(2)
        kn_client = UserBot(
            name=str(user_id),
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session_string,
            in_memory=True,
        )
        try:
            await kn_client.start()
            for modul in _PLUGINS:
                importlib.reload(importlib.import_module(f"plugins.{modul}"))
        except Exception as e:
            logger.error(f"Error Client: {str(e)}")
        if not await dB.get_expired_date(kn_client.me.id):
            await setExpiredUser(kn_client.me.id)
        await dB.add_ubot(
            user_id=int(kn_client.me.id),
            session_string=session_string,
        )
        if not user_id == kn_client.me.id:
            navy._ubot.remove(kn_client)
            await dB.remove_ubot(kn_client.me.id)
            await kn_client.log_out()
            return await bot_msg.edit(
                f"<blockquote><b>Gunakan akun anda sendiri, bukan orang lain!!</b></blockquote>"
            )
        user_token = await dB.generate_token(kn_client.me.id)
        await asyncio.sleep(1)
        seles = await dB.get_list_from_var(BOT_ID, "SELLER")
        if kn_client.me.id not in seles:
            try:
                AKSES_DEPLOY.remove(kn_client.me.id)
            except Exception:
                pass
        for chat in WAJIB_JOIN:
            try:
                await kn_client.join_chat(chat)
            except Exception:
                pass
        prefix = navy.get_prefix(kn_client.me.id)
        keyb = ButtonUtils.start_menu(is_admin=False)
        exp = await dB.get_expired_date(kn_client.me.id)
        PLAN = (
            "basic" if await dB.get_var(kn_client.me.id, "plan") == "basic" else "pro"
        )
        expir = exp.astimezone(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M")
        text_done = f"""
<blockquote expandable><b>🔥 {bot.me.mention} Berhasil Di Aktifkan
➡️ Akun: <a href=tg://openmessage?user_id={kn_client.me.id}>{kn_client.me.first_name} {kn_client.me.last_name or ''}</a>
➡️ ID: <code>{kn_client.me.id}</code>
➡️ Plan: <b>{PLAN}</b>
➡️ Prefixes: {' '.join(prefix)}
➡️ Token: <code>{user_token}</code>
➡️ Masa Aktif: {expir}</b></blockquote>

<blockquote expandable><b>Token kamu berfungsi untuk mengklaim garansi ubot, 
jika kamu ingin berpindah akun atau akunmu dibanned oleh pihak Telegram.
Mohon simpan Token kamu dengan aman.</b></blockquote>"""
        await bot_msg.edit(text_done, disable_web_page_preview=True, reply_markup=keyb)
        return await client.send_message(
            LOG_SELLER,
            f"""
<b>❏ Notifikasi Userbot Aktif</b>
<b>├ Akun :</b> <a href=tg://user?id={kn_client.me.id}>{kn_client.me.first_name} {kn_client.me.last_name or ''}</a> 
<b>├ ID :</b> <code>{kn_client.me.id}</code>
<b>╰ User Token :</b> <code>{user_token}</code>""",
            reply_markup=ikb(
                [
                    [
                        (
                            "Cek Kadaluarsa",
                            f"cek_masa_aktif {kn_client.me.id}",
                            "callback_data",
                        )
                    ]
                ]
            ),
            disable_web_page_preview=True,
        )
    except Exception:
        logger.error(f"ERROR Create Users: {traceback.format_exc()}")
