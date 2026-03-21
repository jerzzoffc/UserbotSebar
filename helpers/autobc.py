
import asyncio
import random
import traceback
from datetime import datetime

from pyrogram.errors import FloodPremiumWait, FloodWait, UserBannedInChannel

from clients import bot, navy
from config import BLACKLIST_GCAST
from database import dB
from logs import logger

from .emoji_logs import Emoji

MAX_CONCURRENT_BROADCAST = 5
AUTOBC_STATUS = []


async def get_auto_gcast_messages(client):
    entries = await dB.get_var(client.me.id, "AUTO_GCAST") or []
    return [await client.get_messages("me", int(e["message_id"])) for e in entries]

async def safe_send_message(selected_msg, chat_id, watermark=None):
    thread_id = await dB.get_var(chat_id, "SELECTED_TOPIC") or None
    try:
        client = selected_msg._client

        if watermark:
            text = selected_msg.text
            caption = selected_msg.caption

            if text:
                await client.send_message(
                    chat_id, f"{text}\n\n{watermark}", message_thread_id=thread_id
                )
            elif caption:
                media_types = [
                    ("photo", selected_msg.photo),
                    ("video", selected_msg.video),
                    ("animation", selected_msg.animation),
                    ("audio", selected_msg.audio),
                    ("document", selected_msg.document),
                    ("sticker", selected_msg.sticker),
                ]

                file_id = None
                for media_type, media_obj in media_types:
                    if media_obj:
                        file_id = media_obj.file_id
                        break

                if file_id:
                    await client.send_cached_media(
                        chat_id,
                        file_id,
                        caption=f"{caption}\n\n{watermark}",
                        message_thread_id=thread_id,
                    )
            else:
                # Handle media tanpa caption
                media_types = [
                    ("photo", selected_msg.photo),
                    ("video", selected_msg.video),
                    ("animation", selected_msg.animation),
                    ("audio", selected_msg.audio),
                    ("document", selected_msg.document),
                    ("sticker", selected_msg.sticker),
                ]

                file_id = None
                for media_type, media_obj in media_types:
                    if media_obj:
                        file_id = media_obj.file_id
                        break

                if file_id:
                    await client.send_cached_media(
                        chat_id, file_id, caption=watermark, message_thread_id=thread_id
                    )
        else:
            await selected_msg.copy(chat_id, message_thread_id=thread_id)

        await asyncio.sleep(0.1)
        return True

    except (FloodWait, FloodPremiumWait) as e:
        await asyncio.sleep(e.value)
        return await safe_send_message(selected_msg, chat_id, watermark)
    except UserBannedInChannel:
        return "banned"
    except Exception:
        return False


async def sending_message(client):
    try:
        messages = await get_auto_gcast_messages(client)
    except OSError:
        logger.error(f"Koneksi {client.me.id} putus")
        if client.me.id in AUTOBC_STATUS:
            AUTOBC_STATUS.remove(client.me.id)
        return
    if not messages:
        return
    while client.me.id in AUTOBC_STATUS:
        try:
            em = Emoji(client)
            await em.get()
            plan = await dB.get_var(client.me.id, "plan")
            watermark = None
            if plan != "is_pro":
                watermark = f"<blockquote><b>{em.robot}AutoBC by @{bot.username}</b></blockquote>"
            sem = asyncio.Semaphore(MAX_CONCURRENT_BROADCAST)
            delay = await dB.get_var(client.me.id, "DELAY_GCAST") or 300
            done = await dB.get_var(client.me.id, "ROUNDS") or 0
            group, failed = 0, 0
            blacklist = set(
                await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST") or []
            ) | set(BLACKLIST_GCAST)

            selected_msg = random.choice(messages)
            peer = client._get_my_peer.get(client.me.id)
            chats = (
                peer.get("group", [])
                if peer and peer.get("group")
                else await client.get_chat_id("group")
            )

            async def send_msg(chat_id):
                nonlocal group, failed
                if chat_id in blacklist:
                    return
                async with sem:
                    result = await safe_send_message(selected_msg, chat_id, watermark)
                if result == True:
                    group += 1
                elif result == "banned":
                    failed += 1
                    await client.send_message(
                        "me",
                        "**⚠️ Your account has limited access**\nAutoBC has been disabled.",
                    )
                    await dB.remove_var(client.me.id, "AUTOBC")
                    if client.me.id in AUTOBC_STATUS:
                        AUTOBC_STATUS.remove(client.me.id)
                else:
                    failed += 1

            print(f"Running autobc for {client.me.id}")
            await asyncio.gather(*(send_msg(chat_id) for chat_id in chats))
            done += 1
            await dB.set_var(client.me.id, "ROUNDS", done)
            await dB.set_var(client.me.id, "SUCCES_GROUP", group)
            await dB.set_var(client.me.id, "LAST_TIME", datetime.utcnow().timestamp())
            summary = (
                f"<b><i>{em.warn}Autobc Done\n"
                f"{em.sukses}Berhasil : {group} Chat\n"
                f"{em.gagal}Gagal : {failed} Chat\n"
                f"{em.msg}Putaran Ke {done} Delay {delay} detik</i></b>"
            )
            try:
                await client.send_message("me", summary)
            except Exception:
                await dB.remove_var(client.me.id, "AUTOBC")
                if client.me.id in AUTOBC_STATUS:
                    AUTOBC_STATUS.remove(client.me.id)
            await asyncio.sleep(int(delay))
        except Exception:
            logger.error(traceback.format_exc())


async def AutoBC():
    logger.info("✅ AutoBC tasks started")
    while True:
        for client in navy._ubot:
            if (
                await dB.get_var(client.me.id, "AUTOBC")
                and client.me.id not in AUTOBC_STATUS
            ):
                last_time = await dB.get_var(client.me.id, "LAST_TIME") or 0
                delay = await dB.get_var(client.me.id, "DELAY_GCAST") or 300
                now = datetime.utcnow().timestamp()

                elapsed = now - last_time
                if elapsed < int(delay):
                    wait_time = int(delay) - int(elapsed)
                    logger.info(
                        f"⏳ Menunggu {wait_time} detik sebelum AutoBC {client.me.id} mulai."
                    )
                    await asyncio.sleep(wait_time)

                AUTOBC_STATUS.append(client.me.id)
                asyncio.create_task(sending_message(client))
        await asyncio.sleep(30)
"""

import asyncio
import random
import traceback
from datetime import datetime
from typing import Dict, Set

from pyrogram.errors import FloodPremiumWait, FloodWait, UserBannedInChannel

from clients import bot, navy
from config import BLACKLIST_GCAST
from database import dB
from logs import logger

from .emoji_logs import Emoji

MAX_CONCURRENT_BROADCAST = 5
AUTOBC_STATUS: Set[int] = set()
# Cache untuk menyimpan data yang sering diakses
CACHE: Dict[int, Dict] = {}
CACHE_TIMEOUT = 300  # 5 menit


async def get_cached_var(client_id: int, key: str):
    current_time = datetime.utcnow().timestamp()

    if (
        client_id not in CACHE
        or current_time - CACHE[client_id].get("last_update", 0) > CACHE_TIMEOUT
    ):
        # Refresh cache
        CACHE[client_id] = {
            "AUTOBC": await dB.get_var(client_id, "AUTOBC"),
            "DELAY_GCAST": await dB.get_var(client_id, "DELAY_GCAST") or 300,
            "plan": await dB.get_var(client_id, "plan"),
            "BLACKLIST_GCAST": set(
                await dB.get_list_from_var(client_id, "BLACKLIST_GCAST") or []
            )
            | set(BLACKLIST_GCAST),
            "last_update": current_time,
        }

    return CACHE[client_id].get(key)


async def get_auto_gcast_messages(client):
    client_id = client.me.id
    if client_id in CACHE and "auto_gcast_messages" in CACHE[client_id]:
        return CACHE[client_id]["auto_gcast_messages"]

    entries = await dB.get_var(client_id, "AUTO_GCAST") or []
    messages = [await client.get_messages("me", int(e["message_id"])) for e in entries]

    if client_id not in CACHE:
        CACHE[client_id] = {}
    CACHE[client_id]["auto_gcast_messages"] = messages
    CACHE[client_id]["auto_gcast_last_update"] = datetime.utcnow().timestamp()

    return messages


async def safe_send_message(selected_msg, chat_id, watermark=None):
    thread_id = await dB.get_var(chat_id, "SELECTED_TOPIC") or None
    try:
        client = selected_msg._client

        if watermark:
            text = selected_msg.text
            caption = selected_msg.caption

            if text:
                await client.send_message(
                    chat_id, f"{text}\n\n{watermark}", message_thread_id=thread_id
                )
            elif caption:
                # Cari file_id berdasarkan media type
                media_types = [
                    ("photo", selected_msg.photo),
                    ("video", selected_msg.video),
                    ("animation", selected_msg.animation),
                    ("audio", selected_msg.audio),
                    ("document", selected_msg.document),
                    ("sticker", selected_msg.sticker),
                ]

                file_id = None
                for media_type, media_obj in media_types:
                    if media_obj:
                        file_id = media_obj.file_id
                        break

                if file_id:
                    await client.send_cached_media(
                        chat_id,
                        file_id,
                        caption=f"{caption}\n\n{watermark}",
                        message_thread_id=thread_id,
                    )
            else:
                # Handle media tanpa caption
                media_types = [
                    ("photo", selected_msg.photo),
                    ("video", selected_msg.video),
                    ("animation", selected_msg.animation),
                    ("audio", selected_msg.audio),
                    ("document", selected_msg.document),
                    ("sticker", selected_msg.sticker),
                ]

                file_id = None
                for media_type, media_obj in media_types:
                    if media_obj:
                        file_id = media_obj.file_id
                        break

                if file_id:
                    await client.send_cached_media(
                        chat_id, file_id, caption=watermark, message_thread_id=thread_id
                    )
        else:
            await selected_msg.copy(chat_id, message_thread_id=thread_id)

        await asyncio.sleep(0.1)  # Reduced sleep time
        return True

    except (FloodWait, FloodPremiumWait) as e:
        await asyncio.sleep(e.value)
        return await safe_send_message(selected_msg, chat_id, watermark)
    except UserBannedInChannel:
        return "banned"
    except Exception:
        return False


async def process_batch(client, selected_msg, chat_ids, watermark, sem, blacklist):
    group, failed = 0, 0
    banned_detected = False

    async def send_to_chat(chat_id):
        nonlocal group, failed, banned_detected
        if banned_detected or chat_id in blacklist:
            return

        async with sem:
            result = await safe_send_message(selected_msg, chat_id, watermark)

        if result == True:
            group += 1
        elif result == "banned":
            failed += 1
            banned_detected = True
            await client.send_message(
                "me",
                "**⚠️ Your account has limited access**\nAutoBC has been disabled.",
            )
            await dB.remove_var(client.me.id, "AUTOBC")
            if client.me.id in AUTOBC_STATUS:
                AUTOBC_STATUS.discard(client.me.id)
        else:
            failed += 1

    # Process in smaller batches to avoid overwhelming
    batch_size = 50
    for i in range(0, len(chat_ids), batch_size):
        batch = chat_ids[i : i + batch_size]
        await asyncio.gather(*(send_to_chat(chat_id) for chat_id in batch))
        await asyncio.sleep(0.5)  # Small delay between batches

    return group, failed, banned_detected


async def sending_message(client):
    client_id = client.me.id

    try:
        messages = await get_auto_gcast_messages(client)
        if not messages:
            return

        while client_id in AUTOBC_STATUS:
            try:
                # Get data from cache
                delay = await get_cached_var(client_id, "DELAY_GCAST")
                plan = await get_cached_var(client_id, "plan")
                blacklist = await get_cached_var(client_id, "BLACKLIST_GCAST")

                em = Emoji(client)
                await em.get()

                watermark = None
                if plan != "is_pro":
                    watermark = f"<blockquote><b>{em.robot}AutoBC by @{bot.username}</b></blockquote>"

                selected_msg = random.choice(messages)

                # Get chats
                peer = client._get_my_peer.get(client_id)
                chats = (
                    peer.get("group", [])
                    if peer and peer.get("group")
                    else await client.get_chat_id("group")
                )

                if not chats:
                    await asyncio.sleep(int(delay))
                    continue

                sem = asyncio.Semaphore(MAX_CONCURRENT_BROADCAST)

                # Process chats in batches
                group, failed, banned_detected = await process_batch(
                    client, selected_msg, chats, watermark, sem, blacklist
                )

                if banned_detected:
                    break

                # Update database
                done = (await dB.get_var(client_id, "ROUNDS") or 0) + 1
                await asyncio.gather(
                    dB.set_var(client_id, "ROUNDS", done),
                    dB.set_var(client_id, "SUCCES_GROUP", group),
                    dB.set_var(client_id, "LAST_TIME", datetime.utcnow().timestamp()),
                )

                # Send summary
                summary = (
                    f"<b><i>{em.warn}Autobc Done\n"
                    f"{em.sukses}Berhasil : {group} Chat\n"
                    f"{em.gagal}Gagal : {failed} Chat\n"
                    f"{em.msg}Putaran Ke {done} Delay {delay} detik</i></b>"
                )

                try:
                    await client.send_message("me", summary)
                except Exception:
                    await dB.remove_var(client_id, "AUTOBC")
                    AUTOBC_STATUS.discard(client_id)
                    break

                await asyncio.sleep(int(delay))

            except Exception as e:
                logger.error(
                    f"Error in sending_message for {client_id}: {traceback.format_exc()}"
                )
                await asyncio.sleep(10)  # Prevent tight error loop

    except OSError:
        logger.error(f"Koneksi {client_id} putus. Remove from autobc")
        AUTOBC_STATUS.discard(client_id)
    except Exception as e:
        logger.error(f"Unexpected error in sending_message: {traceback.format_exc()}")
        AUTOBC_STATUS.discard(client_id)


MAX_CONCURRENT_AUTOBC_TASKS = 10
current_running_tasks = 0
auto_bc_queue = asyncio.Queue()


async def AutoBC():
    global current_running_tasks
    logger.info("✅ AutoBC tasks started")

    waiting_clients = {}

    while True:
        try:
            current_time = datetime.utcnow().timestamp()

            for client_id, wait_until in list(waiting_clients.items()):
                if current_time >= wait_until:
                    client = next((c for c in navy._ubot if c.me.id == client_id), None)
                    if client and client_id not in AUTOBC_STATUS:
                        await auto_bc_queue.put((client_id, client))
                    del waiting_clients[client_id]

            for client in navy._ubot:
                client_id = client.me.id

                if client_id in AUTOBC_STATUS or client_id in waiting_clients:
                    continue

                auto_bc_enabled = await get_cached_var(client_id, "AUTOBC")
                if not auto_bc_enabled:
                    continue

                last_time = await dB.get_var(client_id, "LAST_TIME") or 0
                delay = await get_cached_var(client_id, "DELAY_GCAST")

                elapsed = current_time - last_time
                if elapsed < int(delay):
                    wait_time = int(delay) - elapsed

                    if wait_time > 30:
                        waiting_clients[client_id] = current_time + wait_time
                        logger.info(
                            f"⏳ Added {client_id} to waitlist for {wait_time:.1f}s"
                        )
                    else:
                        await auto_bc_queue.put((client_id, client))
                else:
                    await auto_bc_queue.put((client_id, client))

            while (
                not auto_bc_queue.empty()
                and current_running_tasks < MAX_CONCURRENT_AUTOBC_TASKS
            ):
                client_id, client = await auto_bc_queue.get()
                if client_id not in AUTOBC_STATUS:
                    AUTOBC_STATUS.add(client_id)
                    current_running_tasks += 1
                    asyncio.create_task(run_autobc_with_limit(client))

            await asyncio.sleep(10)

        except Exception as e:
            logger.error(f"Error in AutoBC main loop: {traceback.format_exc()}")
            await asyncio.sleep(30)


async def run_autobc_with_limit(client):
    global current_running_tasks
    try:
        await sending_message(client)
    finally:
        current_running_tasks -= 1
        if client.me.id in AUTOBC_STATUS:
            AUTOBC_STATUS.discard(client.me.id)
"""