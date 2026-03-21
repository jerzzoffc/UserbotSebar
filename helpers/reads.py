import asyncio

from pyrogram import enums
from pyrogram.errors import (ChannelPrivate, FloodPremiumWait, FloodWait,
                             PeerIdInvalid, UserBannedInChannel)
from pyrogram.raw.functions.messages import ReadMentions

from clients import navy
from database import dB
from logs import logger

CHAT_TYPES = {
    "READ_GC": [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP],
    "READ_CH": [enums.ChatType.CHANNEL],
    "READ_US": [enums.ChatType.PRIVATE],
    "READ_BOT": [enums.ChatType.BOT],
    "READ_ALL": [
        enums.ChatType.GROUP,
        enums.ChatType.SUPERGROUP,
        enums.ChatType.CHANNEL,
        enums.ChatType.PRIVATE,
        enums.ChatType.BOT,
    ],
    "READ_MENTION": [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP],
}


async def safe_read_history(client, chat_id):
    try:
        await client.read_chat_history(chat_id, max_id=0)
    except (ChannelPrivate, PeerIdInvalid, UserBannedInChannel):
        pass
    except (FloodWait, FloodPremiumWait) as e:
        await asyncio.sleep(e.value)
        await safe_read_history(client, chat_id)


async def safe_invoke_read_mentions(client, chat_id):
    try:
        await client.invoke(ReadMentions(peer=await client.resolve_peer(chat_id)))
    except (ChannelPrivate, PeerIdInvalid, UserBannedInChannel):
        pass
    except (FloodWait, FloodPremiumWait) as e:
        await asyncio.sleep(e.value)
        await safe_invoke_read_mentions(client, chat_id)


async def auto_read(client, mode):
    delay = await dB.get_var(client.me.id, "TIME_READ") or 3600
    while True:
        if not await dB.get_var(client.me.id, mode):
            await asyncio.sleep(360)
            continue
        try:
            async for dialog in client.get_dialogs():
                if dialog.chat.type not in CHAT_TYPES[mode]:
                    continue
                if mode == "READ_MENTION":
                    await safe_invoke_read_mentions(client, dialog.chat.id)
                else:
                    await safe_read_history(client, dialog.chat.id)
        except Exception:
            await dB.remove_var(client.me.id, mode)
        await asyncio.sleep(delay)


async def ReadUser():
    logger.info("✅ AutoRead task started.")
    for client in navy._ubot:
        for mode in CHAT_TYPES:
            asyncio.create_task(auto_read(client, mode))
