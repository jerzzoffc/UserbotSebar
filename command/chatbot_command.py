import asyncio
import random
import time
import traceback

from pyrogram import enums, errors

import config
from clients import navy
from database import dB
from helpers import (MessageFilter, Tools, get_cached_list, reply_same_type,
                     url_mmk)

userbot_ids = set()

blacklisted_chats = set()

validator = MessageFilter()

SEMAPHORE = asyncio.Semaphore(10)
last_msg_cache = {}
message_queue = {}


DEFAULT_ROLE = "lu adalah manusia dengan karakter sikap jutek, ngeselin. balas pesan harus pendek dan nyolot dikit serta gunakan kata kata yang toxic. serta balaslah pesan menggunakan huruf kecil disemua teks dan balaslah pesan sesingkat mungkin."


async def gen_text(client, message):
    text = (message.text or message.caption).strip()
    if not text:
        return

    role = await dB.get_var(client.me.id, "ROLE_CHATBOT") or DEFAULT_ROLE
    API_URL = f"https://api-02.ryzumi.vip/api/ai/chatgpt?text={text}&prompt={role}"

    try:
        res = await Tools.fetch.get(API_URL)
        if res.status_code == 200:
            result = res.json().get("result")
            if "%20" in result:
                result = result.replace("%20", " ")
            return result
    except Exception:
        return None


async def get_random_text():
    return await dB.get_var(config.BOT_ID, "CHATBOT_TEXT") or []


async def add_auto_text(text):
    auto_text = await get_random_text()
    auto_text.append(text)
    await dB.set_var(config.BOT_ID, "CHATBOT_TEXT", auto_text)


async def chatbot_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply(
            f"<b>Usage: `{message.text.split()[0]} on | off | status | role | ignoreadmin | reignoreadmin`</b>"
        )

    cmd = message.command[1].lower()

    if cmd == "on":
        if message.chat.type in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
            return await message.reply("<b>Please enable in group.</b>")
        if message.chat.id in await dB.get_list_from_var(client.me.id, "CHATBOT"):
            return await message.reply(f"**Chat already in database.**")
        await dB.add_to_var(client.me.id, "CHATBOT", message.chat.id)
        return await message.reply(f"<b> Chatbot turned on in this group.</b>")

    elif cmd == "off":
        if len(message.command) < 3:
            if message.chat.type in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
                return await message.reply("<b>Please enable in group.</b>")
            chat_id = message.chat.id
            if chat_id not in await dB.get_list_from_var(client.me.id, "CHATBOT"):
                return await message.reply(f"**`{chat_id}` is not found!**")
            await dB.remove_from_var(client.me.id, "CHATBOT", chat_id)
            name = (await client.get_chat(chat_id)).title
            return await message.reply(f"<b>Turned off chatbot for chat: {name}</b>")
        else:
            if message.command[2] == "all":
                for cid in await dB.get_list_from_var(client.me.id, "CHATBOT"):
                    await dB.remove_from_var(client.me.id, "CHATBOT", cid)
                return await message.reply(f"<b>All chatbot group lists cleared.</b>")
            else:
                try:
                    chat_id = int(message.command[2])
                except ValueError:
                    return await message.reply(
                        f"**Invalid chat ID `{message.command[2]}`.**"
                    )
                if chat_id not in await dB.get_list_from_var(client.me.id, "CHATBOT"):
                    return await message.reply(f"`{chat_id}` **Not found!**")
                await dB.remove_from_var(client.me.id, "CHATBOT", chat_id)
                name = (await client.get_chat(chat_id)).title
                return await message.reply(
                    f"<b>Turned off chatbot for chat: {name}</b>"
                )
    elif cmd == "status":
        chats = await dB.get_list_from_var(client.me.id, "CHATBOT")
        if not chats:
            return await message.reply(f"<b>No active groups using chatbot.</b>")
        msg = ""
        for i, chat_id in enumerate(chats, 1):
            try:
                chat = await client.get_chat(chat_id)
                msg += f"<b>{i}. {chat.title} | `{chat.id}`</b>\n"
            except Exception:
                continue
        return await message.reply(msg or f"<b>All active groups inaccessible.</b>")

    elif cmd == "role":
        if not message.reply_to_message:
            return await message.reply(
                f"<b>Usage: reply to a message → `{message.text.split()[0]} role`</b>"
            )
        role = message.reply_to_message.text or message.reply_to_message.caption
        await dB.set_var(client.me.id, "ROLE_CHATBOT", role)
        return await message.reply(f"<b>Role set to:</b> <code>{role}</code>")

    elif cmd == "ignore":
        reply = message.reply_to_message
        try:
            target = reply.from_user.id if reply else message.text.split()[2]
        except (AttributeError, IndexError):
            return await message.reply(
                f"<b>You need to specify a user (either by reply or username/ID)!</b>"
            )
        try:
            user = await client.get_users(target)
        except (
            errors.PeerIdInvalid,
            KeyError,
            errors.UsernameInvalid,
            errors.UsernameNotOccupied,
        ):
            return await message.reply(f"<b>You need meet before interact!!</b>")
        user_id = user.id
        if user_id in await dB.get_list_from_var(client.me.id, "CHATBOT_IGNORE"):
            return await message.reply(f"**User already ignored chatbot.**")
        await dB.add_to_var(client.me.id, "CHATBOT_IGNORE", user_id)
        return await message.reply(
            f"<b>Chatbot will now ignore {user_id} in this group.</b>"
        )
    elif cmd == "reignore":
        reply = message.reply_to_message
        try:
            target = reply.from_user.id if reply else message.text.split()[2]
        except (AttributeError, IndexError):
            return await message.reply(
                f"<b>You need to specify a user (either by reply or username/ID)!</b>"
            )
        try:
            user = await client.get_users(target)
        except (
            errors.PeerIdInvalid,
            KeyError,
            errors.UsernameInvalid,
            errors.UsernameNotOccupied,
        ):
            return await message.reply(f"<b>You need meet before interact!!</b>")
        user_id = user.id
        if user_id not in await dB.get_list_from_var(client.me.id, "CHATBOT_IGNORE"):
            return await message.reply(f"**User not found in database.**")

        await dB.remove_from_var(client.me.id, "CHATBOT_IGNORE_ADMIN", user_id)
        return await message.reply(
            f"<b>Chatbot will now respond {user_id} again in this group.</b>"
        )
    elif cmd == "admin":
        if len(message.command) < 3:
            return await message.reply(f"**Please give query on or off.**")
        query = message.text.split()[2]
        if query.lower() == "on":
            if await dB.get_var(client.me.id, "CHATBOT_ADMIN"):
                await dB.remove_var(client.me.id, "CHATBOT_ADMIN")
                return await message.reply(
                    f"**Chatbot will respond message from admins now.**"
                )
            else:
                return await message.reply(
                    f"**Chatbot respond from admins already enable.**"
                )
        elif query.lower() == "off":
            if not await dB.get_var(client.me.id, "CHATBOT_ADMIN"):
                await dB.set_var(client.me.id, "CHATBOT_ADMIN", True)
                return await message.reply(
                    f"**Chatbot will pass message from admins now.**"
                )
            else:
                return await message.reply(
                    f"**Chatbot respond from admins already disable.**"
                )
        else:
            return await message.reply(f"**Please give query on or off.**")
    elif cmd == "reply":
        if len(message.command) < 3:
            return await message.reply(f"**Please give query on or off.**")
        query = message.text.split()[2]
        if query.lower() == "on":
            if not await dB.get_var(client.me.id, "CHATBOT_REPLY"):
                await dB.set_var(client.me.id, "CHATBOT_REPLY", True)
                return await message.reply(
                    f"**Chatbot will respond all chats if someone reply your messages.**"
                )
            else:
                return await message.reply(
                    f"**Chatbot reply user for all chats already enable.**"
                )
        elif query.lower() == "off":
            if await dB.get_var(client.me.id, "CHATBOT_REPLY"):
                await dB.remove_var(client.me.id, "CHATBOT_REPLY")
                return await message.reply(
                    f"**Chatbot reply user for all chats disable.**"
                )
            else:
                return await message.reply(
                    f"**Chatbot reply user for all chats already disable.**"
                )
        else:
            return await message.reply(f"**Please give query on or off.**")

    else:
        return await message.reply(
            f"<b>Usage: `{message.text.split()[0]} on | off | status | role | ignoreadmin | reignoreadmin`</b>"
        )


async def auto_reply_trigger(client, message):
    text = message.text or message.caption
    if (
        message.reply_to_message
        and (message.reply_to_message.from_user or message.reply_to_message.sender_chat)
        and (
            message.reply_to_message.from_user or message.reply_to_message.sender_chat
        ).id
        == client.me.id
    ):
        if await dB.get_var(client.me.id, "CHATBOT_REPLY"):
            if text:
                for word in config.BLACKLIST_KATA:
                    if word in text:
                        return
                if url_mmk(text) or validator.is_text_abnormal(text):
                    return
                await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
                response = await gen_text(client, message)

                if response:
                    try:
                        await message.reply(response)
                        await add_auto_text(response)
                    except errors.FloodWait as e:
                        await asyncio.sleep(e.value)
                        await message.reply(response)
                        await add_auto_text(response)
                else:
                    fallback = await get_random_text()
                    if fallback:
                        await message.reply(random.choice(fallback))

                return await client.send_chat_action(
                    message.chat.id, enums.ChatAction.CANCEL
                )
            else:
                return await reply_same_type(message)
    elif client.me.username and (
        (message.text and client.me.username in message.text)
        or (message.caption and client.me.username in message.caption)
    ):
        if not await dB.get_var(client.me.id, "CHATBOT_REPLY"):
            return
        mention = message.from_user.mention()
        caption_text = (message.caption or "").replace(client.me.username, mention)
        if message.text:
            for word in config.BLACKLIST_KATA:
                if word in text:
                    return
            if url_mmk(text) or validator.is_text_abnormal(text):
                return
            await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
            response = await gen_text(client, message)

            if response:
                try:
                    await message.reply(response)
                    await add_auto_text(response)
                except errors.FloodWait as e:
                    await asyncio.sleep(e.value)
                    await message.reply(response)
                    await add_auto_text(response)
            else:
                fallback = await get_random_text()
                if fallback:
                    await message.reply(random.choice(fallback))

            return await client.send_chat_action(
                message.chat.id, enums.ChatAction.CANCEL
            )
        else:
            return await reply_same_type(message, mention_text=caption_text)


async def chatbot_trigger(client, message):
    if not message.from_user or not message.chat:
        return

    if message.chat.id not in await dB.get_list_from_var(client.me.id, "CHATBOT"):
        return

    if message.from_user.id in await dB.get_list_from_var(
        client.me.id, "CHATBOT_IGNORE"
    ):
        return

    if await dB.get_var(client.me.id, "CHATBOT_ADMIN"):
        if message.from_user.id in await client.admin_list(message):
            return

    text = message.text or message.caption
    if text:
        for word in config.BLACKLIST_KATA:
            if word in text:
                return
        if url_mmk(text) or validator.is_text_abnormal(text):
            return

        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        response = await gen_text(client, message)

        if response:
            try:
                await message.reply(response)
                await add_auto_text(response)
            except errors.FloodWait as e:
                await asyncio.sleep(e.value)
                await message.reply(response)
                await add_auto_text(response)
        else:
            fallback = await get_random_text()
            if fallback:
                await message.reply(random.choice(fallback))

        return await client.send_chat_action(message.chat.id, enums.ChatAction.CANCEL)


async def get_last_message(client, chat_id, ttl=30):
    key = (client.me.id, chat_id)
    if key in last_msg_cache and time.time() - last_msg_cache[key][0] < ttl:
        return last_msg_cache[key][1]
    async for msg in client.get_chat_history(chat_id, limit=1):
        last_msg_cache[key] = (time.time(), msg)
        return msg


async def safe_send(client, message, text):
    try:
        await message.reply(text)
    except errors.FloodWait as e:
        await asyncio.sleep(e.value)
        await message.reply(text)


async def limited_chatbot_trigger(client, msg):
    async with SEMAPHORE:
        await chatbot_trigger(client, msg)


async def queue_message(client, message):
    q = message_queue.setdefault(client.me.id, asyncio.Queue())
    await q.put(message)
    if q.qsize() == 1:
        asyncio.create_task(process_queue(client, q))


async def process_queue(client, q):
    while not q.empty():
        msg = await q.get()
        await limited_chatbot_trigger(client, msg)
        await asyncio.sleep(0.5)


async def ChatbotTask():
    while True:
        try:
            for client in navy._ubot:
                chats = await get_cached_list(
                    dB.get_list_from_var, client.me.id, "CHATBOT"
                )
                for chat_id in chats:
                    if chat_id in blacklisted_chats:
                        continue
                    try:
                        msg = await get_last_message(client, chat_id)
                        if not msg or not msg.text:
                            continue
                        await queue_message(client, msg)
                    except (errors.ChatWriteForbidden, errors.ChannelInvalid):
                        print(f"Access issue {client.me.id} in {chat_id}, deleted.")
                        await dB.remove_from_var(client.me.id, "CHATBOT", chat_id)
                        continue
                    except Exception as e:
                        print(f"Error handling {client.me.id} chat {chat_id}: {e}")
                        await asyncio.sleep(1)
                        continue
            await asyncio.sleep(60)
        except Exception:
            print(f"error: {traceback.format_exc()}")
