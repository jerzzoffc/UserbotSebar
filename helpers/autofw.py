import asyncio
from datetime import datetime

from pyrogram.errors import FloodPremiumWait, FloodWait, UserBannedInChannel

from clients import navy
from config import BLACKLIST_GCAST
from database import dB
from logs import logger

from .emoji_logs import Emoji
from .tools import Tools

MAX_CONCURRENT_BROADCAST = 5
AUTOFW_STATUS = []


async def safe_forward(client, chat_id, chatids, messageids):
    try:
        await client.forward_messages(chat_id, chatids, message_ids=messageids)
        await asyncio.sleep(0.5)
        return True
    except (FloodWait, FloodPremiumWait) as e:
        logger.warning(f"FloodWait {e.value}s on chat {chat_id}")
        await asyncio.sleep(e.value)
        try:
            await client.forward_messages(chat_id, chatids, message_ids=messageids)
            await asyncio.sleep(0.5)
            return True
        except Exception:
            return False
    except UserBannedInChannel:
        return "banned"
    except Exception:
        return False


async def send_forward(client):
    while client.me.id in AUTOFW_STATUS:
        em = Emoji(client)
        await em.get()
        sem = asyncio.Semaphore(MAX_CONCURRENT_BROADCAST)

        delay = await dB.get_var(client.me.id, "DELAY_AUTOFW") or 300
        link = await dB.get_var(client.me.id, "AUTOFW_GCAST_TEXT")

        if not link:
            return

        logger.info(f"🔁 Running AutoFW for {client.me.id}")
        chatids, messageids = Tools.get_link(link)
        done = await dB.get_var(client.me.id, "ROUNDSFW") or 0
        group, failed = 0, 0

        blacklist = set(
            await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST") or []
        ) | set(BLACKLIST_GCAST)

        peer = client._get_my_peer.get(client.me.id)
        chats = (
            peer.get("group", [])
            if peer and peer.get("group")
            else await client.get_chat_id("group")
        )

        async def forward_msg(chat_id):
            nonlocal group, failed
            if chat_id in blacklist:
                return
            async with sem:
                result = await safe_forward(client, chat_id, chatids, messageids)

            if result == True:
                group += 1
            elif result == "banned":
                failed += 1
                await client.send_message(
                    "me",
                    "**⚠️ Your account has limited access**\nAutoFW has been disabled.",
                )
                await dB.remove_var(client.me.id, "AUTOFW")
                if client.me.id in AUTOFW_STATUS:
                    AUTOFW_STATUS.remove(client.me.id)
            else:
                failed += 1

        await asyncio.gather(*(forward_msg(chat_id) for chat_id in chats))

        done += 1
        await dB.set_var(client.me.id, "ROUNDSFW", done)
        await dB.set_var(client.me.id, "SUCCESFW_GROUP", group)
        await dB.set_var(client.me.id, "LAST_TIME_FW", datetime.utcnow().timestamp())

        summary = (
            f"<b><i>{em.warn}AUTOFW Done\n"
            f"{em.sukses}Berhasil : {group} Chat\n"
            f"{em.gagal}Gagal : {failed} Chat\n"
            f"{em.msg}Putaran Ke {done} Delay {delay} detik</i></b>"
        )
        try:
            await client.send_message("me", summary)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await client.send_message("me", summary)
        except Exception as e:
            logger.error(f"Gagal kirim summary ke 'me': {e}")
            await dB.remove_var(client.me.id, "AUTOFW")
            if client.me.id in AUTOFW_STATUS:
                AUTOFW_STATUS.remove(client.me.id)

        await asyncio.sleep(int(delay))


"""
async def AutoFW():
    logger.info("✅ AutoFW task started")
    while True:
        for client in navy._ubot:
            if (
                await dB.get_var(client.me.id, "AUTOFW")
                and client.me.id not in AUTOFW_STATUS
            ):
                AUTOFW_STATUS.append(client.me.id)
                asyncio.create_task(send_forward(client))
        await asyncio.sleep(30)
"""


async def AutoFW():
    logger.info("✅ AutoFW tasks started")
    while True:
        for client in navy._ubot:
            if (
                await dB.get_var(client.me.id, "AUTOFW")
                and client.me.id not in AUTOFW_STATUS
            ):
                last_time = await dB.get_var(client.me.id, "LAST_TIME_FW") or 0
                delay = await dB.get_var(client.me.id, "DELAY_AUTOFW") or 300
                now = datetime.utcnow().timestamp()

                elapsed = now - last_time
                if elapsed < int(delay):
                    wait_time = int(delay) - int(elapsed)
                    logger.info(
                        f"⏳ Menunggu {wait_time} detik sebelum AutoFW {client.me.id} mulai."
                    )
                    await asyncio.sleep(wait_time)

                AUTOFW_STATUS.append(client.me.id)
                asyncio.create_task(send_forward(client))
        await asyncio.sleep(30)
