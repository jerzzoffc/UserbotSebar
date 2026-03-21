import asyncio
import os
import sys
import traceback
import zipfile
from datetime import datetime

from pyrogram import enums
from pyrogram.helpers import kb
from pytz import timezone

from clients import bot, navy
from config import (BOT_ID, BOT_NAME, IS_JASA_PRIVATE, LOG_BACKUP, LOG_SELLER,
                    OWNER_ID)
from database import DB_PATH, dB
from logs import logger

from .message import Message
from .tools import Tools

waktu_jkt = timezone("Asia/Jakarta")


async def load_user_allchats(client):
    private = []
    group = []
    globall = []
    all = []
    bots = []
    try:
        async for dialog in client.get_dialogs():
            try:
                if dialog.chat.type == enums.ChatType.PRIVATE:
                    private.append(dialog.chat.id)
                elif dialog.chat.type in (
                    enums.ChatType.GROUP,
                    enums.ChatType.SUPERGROUP,
                ):
                    group.append(dialog.chat.id)
                elif dialog.chat.type in (
                    enums.ChatType.GROUP,
                    enums.ChatType.SUPERGROUP,
                    enums.ChatType.CHANNEL,
                ):
                    globall.append(dialog.chat.id)
                elif dialog.chat.type in (
                    enums.ChatType.GROUP,
                    enums.ChatType.SUPERGROUP,
                    enums.ChatType.PRIVATE,
                ):
                    all.append(dialog.chat.id)
                if dialog.chat.type == enums.ChatType.BOT:
                    bots.append(dialog.chat.id)
            except Exception:
                continue
    except Exception:
        pass
    return private, group, globall, all, bots


async def installing_user(client):
    private, group, globall, all, bots = await load_user_allchats(client)
    client_id = client.me.id
    client._get_my_peer[client_id] = {
        "private": private,
        "group": group,
        "global": globall,
        "all": all,
        "bot": bots,
    }


async def installPeer():
    try:
        for client in navy._ubot:
            await installing_user(client)
        await bot.send_message(OWNER_ID, "✅ Sukses Install Data Pengguna.")
    except Exception:
        await bot.send_message(OWNER_ID, f"Error installPeer {traceback.format_exc()}")


async def sending_user(user_id):
    try:
        await bot.send_message(
            user_id,
            f"<blockquote><b>Akun anda tidak dapat memberikan Respon!!\n\nHarap Hentikan Sesi Perangkat dengan nama <code>{BOT_NAME}</code>. Lalu, lakukan Re-Deploy atau klik Lanjut Pembuatan Ulang Userbot di bawah (JIKA MERASA ANDA MASIH MEMILIKI SISA WAKTU EXPIRED USERBOT).</b></blockquote>",
            reply_markup=kb(
                [["✨ Pembuatan Ulang Userbot"]],
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
        )
    except Exception:
        return


async def stoped_ubot(userid):
    clients = navy._ubot
    for client in clients:
        if client.me.id == userid:
            await dB.remove_ubot(client.me.id)
            await dB.rem_expired_date(client.me.id)
            await dB.remove_var(client.me.id, "plan")
            await dB.revoke_token(client.me.id, deleted=True)
            navy._get_my_id.remove(client.me.id)
            navy._ubot.remove(client)
            try:
                await client.stop()
                await asyncio.sleep(2)
                return await client.log_out()
            except Exception:
                pass


async def stop_main():
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    logger.info(f"📌 Total task yang akan dihentikan: {len(tasks)}")

    if not tasks:
        logger.info("✅ Tidak ada task yang berjalan.")
        return

    for task in tasks:
        try:
            if not task.done():
                task.cancel()
        except Exception as e:
            logger.error(f"❗ Gagal cancel task: {e}")

    await asyncio.sleep(1)

    loop = asyncio.get_event_loop()
    results = []
    for task in tasks:
        if loop.is_closed():
            logger.warning("⚠️ Loop is closed, skip wait_for.")
            continue
        try:
            result = await asyncio.wait_for(asyncio.shield(task), timeout=5)
            results.append(result)
        except TimeoutError:
            logger.error(
                f"⏳ Timeout saat menghentikan task: {task.get_name() or task}"
            )
            results.append(None)
        except asyncio.CancelledError:
            continue
        except Exception as e:
            logger.error(f"⚠️ Task {task.get_name() or task} mengalami error: {e}")

        logger.info(
            f"Task: {task.get_name()}, Done: {task.done()}, Cancelled: {task.cancelled()}"
        )

    logger.info("⚠️ Menutup database...")
    await Tools.close_fetch()
    await dB.close()

    logger.info("✅ Semua task dihentikan dan database telah ditutup.")


async def restart_process():
    try:
        await stop_main()
        await asyncio.sleep(2)
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        logger.error(f"❌ Gagal restart: {e}")


async def CheckUsers():
    logger.info("✅ CheckUsers task started.")
    while True:
        try:
            total = await dB.get_var(BOT_ID, "total_users")
            current_total = len(navy._ubot)
            if current_total == total:
                await asyncio.sleep(360)
                continue
            now = datetime.now(timezone("Asia/Jakarta"))
            filename = f"{BOT_NAME}_{now.strftime('%Y-%m-%d_%H:%M')}.zip"
            with zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED) as zipf:
                if os.path.exists(".env"):
                    zipf.write(os.path.abspath(".env"), ".env")
                zipf.write(DB_PATH, os.path.basename(DB_PATH))
            await bot.send_document(
                LOG_BACKUP, filename, caption=now.strftime("%d %B %Y %H:%M")
            )
            os.remove(filename)
            await dB.set_var(BOT_ID, "total_users", current_total)
        except Exception as e:
            await bot.send_message(LOG_SELLER, f"CheckUsers error: {e}")


async def ExpiredSewa():
    logger.info("✅ ExpiredSewa task started.")
    if not IS_JASA_PRIVATE:
        return
    while True:
        try:
            now = datetime.now(timezone("Asia/Jakarta"))
            exp = await dB.get_expired_date(BOT_ID)
            if not exp:
                await asyncio.sleep(360)
                continue
            if now >= exp:
                await bot.send_message(
                    OWNER_ID,
                    "<blockquote><b>Maaf, masa aktif Bot Sewa Private Anda sudah habis!!\nSilahkan kontak @Jhainhere untuk memperpanjang masa aktif bot.</b></blockquote>",
                )
                await dB.rem_expired_date(BOT_ID)
                await asyncio.sleep(360)
                continue
        except Exception:
            logger.error(f"ERROR EXPIRED SEWA: {traceback.format_exc()}")
            continue


async def handle_user_expired(client, msg=None):
    try:
        await client.unblock_user(bot.me.username)
        if msg:
            await bot.send_message(client.me.id, msg)
    except Exception:
        pass

    await dB.remove_ubot(client.me.id)
    await dB.remove_var(client.me.id, "plan")
    await dB.rem_expired_date(client.me.id)
    await dB.revoke_token(client.me.id, deleted=True)

    navy._get_my_id.remove(client.me.id)
    navy._ubot.remove(client)

    await client.stop()
    await asyncio.sleep(2)
    try:
        await client.log_out()
    except Exception:
        pass


async def ExpiredUser():
    logger.info("✅ ExpiredUser task started.")
    while True:
        for client in navy._ubot.copy():
            try:
                now = datetime.now(timezone("Asia/Jakarta"))
                exp = await dB.get_expired_date(client.me.id)
                if now >= exp:
                    msg = Message.expired_message(client)
                    await bot.send_message(LOG_SELLER, msg)
                    await handle_user_expired(client, msg)
            except TypeError:
                logger.error(f"Expired error {client.me.id}: Deleted on database")
                await handle_user_expired(client)
                await bot.send_message(
                    LOG_SELLER, f"Expired error {client.me.id}: Deleted on database"
                )
            except Exception:
                await handle_user_expired(client)
                logger.error(f"Expired error {client.me.id}: {traceback.format_exc()}")
                await bot.send_message(
                    LOG_SELLER,
                    f"Deleted users {client.me.id}: {traceback.format_exc()}",
                )
        await asyncio.sleep(360)

