import asyncio

from pyrogram import enums, filters
from pyrogram.errors import FloodPremiumWait, FloodWait
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

from clients import bot, navy
from config import (BOT_ID, FAKE_DEVS, IS_JASA_PRIVATE, KYNAN, LOG_SELLER,
                    OWNER_ID, SUDO_OWNERS)
from database import dB
from logs import logger

from .emoji_logs import Emoji

trigger = r"^(💬 Jawab Pesan|👤 Akun|❌ Batalkan|✨ Mulai Buat Userbot|❓ Status Akun|🔄 Reset Emoji|🔄 Reset Prefix|🔄 Restart Userbot|🔄 Reset Text|🚀 Updates|👥 Cek User|🛠️ Cek Fitur|↩️ Beranda|✨ Pembuatan Ulang Userbot|💬 Hubungi Admins|✅ Lanjutkan Buat Userbot|🔑 Token|🧩 Plan Basic|💎 Plan Pro|⚡ Plan Lite)"
words = trigger.replace("^(", "").replace(")", "").split("|")
wrapped_words = [f'"{word}"' for word in words]
no_trigger = "[" + ", ".join(wrapped_words) + "]"
no_commands = [
    "💬 Jawab Pesan",
    "🧩 Plan Basic",
    "💎 Plan Pro",
    "🔑 Token",
    "👤 Akun",
    "🎟️ Referral",
    "❌ Batalkan",
    "✨ Mulai Buat Userbot",
    "❓ Status Akun",
    "🔄 Reset Emoji",
    "🔄 Reset Prefix",
    "🔄 Restart Userbot",
    "✅ Lanjutkan Buat Userbot",
    "🔄 Reset Text",
    "🚀 Updates",
    "👥 Cek User",
    "🛠️ Cek Fitur",
    "🤔 Pertanyaan",
    "↩️ Beranda",
    "✨ Pembuatan Ulang Userbot",
    "💬 Hubungi Admins",
    "📃 Saya Setuju",
    "kontol",
    "close",
    "restart",
    "id",
    "button",
    "token",
    "referral",
    "sh",
    "eval",
    "update",
    "restore",
    "backup",
    "reboot",
    "setimg",
    "setads",
    "cancel",
]


async def verified_sudo(_, client, message):
    sudo_users = await dB.get_list_from_var(client.me.id, "SUDOERS")
    is_user = message.from_user or message.sender_chat
    is_self = bool(
        message.from_user
        and message.from_user.is_self
        or getattr(message, "outgoing", False)
    )
    return is_user.id in sudo_users or is_self


async def is_blocked(_, __, message):
    if message.sender_chat:
        return
    return bool(
        message.from_user and message.from_user.status == enums.UserStatus.LONG_AGO
    )


class FILTERS:
    PRIVATE = filters.private
    OWNER = filters.user(OWNER_ID)
    FAKE_DEV2 = filters.user(OWNER_ID)
    DEVELOPER = filters.user(KYNAN) & ~filters.me
    FAKE_DEV = filters.user(FAKE_DEVS) & ~filters.me


class CMD:
    @staticmethod
    def FLOOD_HANDLER(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except (FloodWait, FloodPremiumWait) as e:
                await asyncio.sleep(e.value)
                return await func(*args, **kwargs)

        return wrapper

    @staticmethod
    def EXPIRED(func):
        async def function(client, message):
            if IS_JASA_PRIVATE:
                expired_date = await dB.get_expired_date(BOT_ID)
                user = (
                    message.from_user.id
                    if message.from_user
                    else message.sender_chat.id
                )
                if user in KYNAN:
                    return await func(client, message)
                if expired_date is None:
                    return await message.reply(
                        "<blockquote><b>Maaf, masa aktif Bot Sewa Private Anda sudah habis!!\nSilahkan kontak @Jhainhere untuk memperpanjang masa aktif bot.</b></blockquote>"
                    )
            return await func(client, message)

        return function

    @staticmethod
    def BOT(command, filter=None):
        def wrapper(func):
            message_filters = (
                filters.command(command) & filter
                if filter
                else filters.command(command)
            )

            @bot.on_message(message_filters)
            @CMD.FLOOD_HANDLER
            @CMD.EXPIRED
            async def wrapped_func(client, message):
                user = message.from_user if message.from_user else message.sender_chat
                if user.id in await dB.get_list_from_var(client.me.id, "BANNED_USERS"):
                    return
                return await func(client, message)

            return wrapped_func

        return wrapper

    @staticmethod
    def UBOT(command, filter=None):
        if filter is None:
            filter = filters.create(verified_sudo)

        def wrapper(func):
            module_tag = func.__globals__.get("__MODULES__", "").lower()
            module_is_pro = func.__globals__.get("IS_PRO", None)
            module_is_basic = func.__globals__.get("IS_BASIC", False)

            @navy.on_message(navy.user_prefix(command) & filter)
            @CMD.FLOOD_HANDLER
            @CMD.EXPIRED
            async def wrapped_func(client, message):
                user = message.from_user or message.sender_chat
                sudo_users = await dB.get_list_from_var(client.me.id, "SUDOERS")
                IGNORE_MODULES = await dB.get_var(client.me.id, "IGNORE_MODULES") or []
                IGNORE_SUDO = await dB.get_var(client.me.id, "IGNORE_SUDO") or []
                DISABLED_COMMAND = await dB.get_var(bot.id, "DISABLED_MODULES") or []
                if message.command[0].lower() in DISABLED_COMMAND:
                    logger.warning(
                        f"[SKIPPED] {client.me.id} disable: {message.command[0].lower()}"
                    )
                    return

                if module_tag in IGNORE_MODULES:
                    logger.warning(f"[SKIPPED] {client.me.id} ignore: {module_tag}")
                    return
                if user.id in sudo_users:
                    if module_tag in IGNORE_SUDO:
                        logger.warning(
                            f"[SKIPPED] {message.from_user.id} ignore sudo: {module_tag}"
                        )
                        return

                plan = await dB.get_var(client.me.id, "plan")
                if plan == "is_pro":
                    pass
                elif plan == "basic":
                    if module_is_pro:
                        return
                elif plan == "lite":
                    if module_is_pro or module_is_basic:
                        return

                return await func(client, message)

            return wrapped_func

        return wrapper

    @staticmethod
    def UBOT_REGEX(command, filter=None):
        if filter is None:
            filter = filters.create(verified_sudo)

        def wrapper(func):
            @navy.on_message(filters.regex(command) & filters.me & filter)
            @CMD.FLOOD_HANDLER
            @CMD.EXPIRED
            async def wrapped_func(client, message):

                return await func(client, message)

            return wrapped_func

        return wrapper

    @staticmethod
    def EDITED():
        def wrapper(func):
            @navy.on_edited_message(
                (filters.mentioned & filters.incoming & ~filters.bot & ~filters.via_bot)
                | (filters.private & filters.incoming & ~filters.bot & ~filters.service)
            )
            async def wrapped_func(client, message):

                return await func(client, message)

            return wrapped_func

        return wrapper

    @staticmethod
    def OWNER(func):
        async def function(client, message):
            user = message.from_user if message.from_user else message.sender_chat
            if user.id != OWNER_ID:
                return
            return await func(client, message)

        return function

    @staticmethod
    def NLX(func):
        async def function(client, message):
            user = message.from_user if message.from_user else message.sender_chat
            if user.id not in KYNAN:
                return
            return await func(client, message)

        return function

    @staticmethod
    def FAKE_NLX(func):
        async def function(client, message):
            user = message.from_user if message.from_user else message.sender_chat
            if user.id not in SUDO_OWNERS:
                return
            return await func(client, message)

        return function

    @staticmethod
    def DEV_CMD(command, filter=FILTERS.DEVELOPER):
        def wrapper(func):
            @navy.on_message(filters.command(command, "^") & filter)
            @CMD.FLOOD_HANDLER
            async def wrapped_func(client, message):
                await func(client, message)

            return wrapped_func

        return wrapper

    @staticmethod
    def FAKEDEV(command, filter=FILTERS.FAKE_DEV):
        def wrapper(func):
            module_tag = func.__globals__.get("__MODULES__", "").lower()
            module_is_pro = func.__globals__.get("IS_PRO", None)
            module_is_basic = func.__globals__.get("IS_BASIC", False)

            @navy.on_message(filters.command(command, "c") & filter)
            @CMD.FLOOD_HANDLER
            async def wrapped_func(client, message):
                IGNORE_MODULES = await dB.get_var(client.me.id, "IGNORE_MODULES") or []
                if module_tag in IGNORE_MODULES:
                    print(f"[SKIPPED] {client.me.id} ignore: {module_tag}")
                    return
                plan = await dB.get_var(client.me.id, "plan")
                plan = await dB.get_var(client.me.id, "plan")
                if plan == "is_pro":
                    pass
                elif plan == "basic":
                    if module_is_pro:
                        return
                elif plan == "lite":
                    if module_is_pro or module_is_basic:
                        return
                return await func(client, message)

            return wrapped_func

        return wrapper

    @staticmethod
    def INLINE():
        def wrapper(func):
            @bot.on_inline_query()
            @CMD.FLOOD_HANDLER
            async def wrapped_func(client, inline_query):
                return await func(client, inline_query)

            return wrapped_func

        return wrapper

    @staticmethod
    def CALLBACK():
        def wrapper(func):
            @bot.on_callback_query()
            async def wrapped_func(client, callback_query):
                return await func(client, callback_query)

            return wrapped_func

        return wrapper

    @staticmethod
    def REGEX(command):
        def wrapper(func):
            @bot.on_message(filters.regex(command))
            @CMD.FLOOD_HANDLER
            @CMD.EXPIRED
            async def wrapped_func(client, message):
                return await func(client, message)

            return wrapped_func

        return wrapper

    @staticmethod
    def CHAT_FORWARD(result, bot):
        query_mapping = {
            "OUTGOING": {
                "query": (
                    filters.reply
                    & filters.chat(LOG_SELLER)
                    & ~filters.command(no_commands)
                ),
                "group": 20,
            },
            "INCOMING": {
                "query": (
                    filters.incoming & filters.private & ~filters.command(no_commands)
                ),
                "group": 21,
            },
        }
        result_query = query_mapping.get(result)

        def wrapper(func):
            if result_query:

                async def wrapped_func(client, message):
                    return await func(client, message)

                bot.on_message(result_query["query"], group=int(result_query["group"]))(
                    wrapped_func
                )

                return wrapped_func
            else:
                return func

        return wrapper

    @staticmethod
    def NO_CMD(result, client):
        query_mapping = {
            "PMPERMIT": {
                "query": (
                    filters.private
                    & filters.incoming
                    & ~filters.me
                    & ~filters.contact
                    & ~filters.bot
                    & ~filters.via_bot
                    & ~filters.service
                ),
                "group": 1,
            },
            "LOGS_GROUP": {
                "query": (
                    filters.mentioned
                    & filters.incoming
                    & ~filters.bot
                    & ~filters.via_bot
                    & ~filters.me
                )
                | (
                    filters.private
                    & filters.incoming
                    & ~filters.me
                    & ~filters.bot
                    & ~filters.service
                ),
                "group": 2,
            },
            "AFK": {
                "query": (
                    (filters.mentioned | filters.private)
                    & ~filters.bot
                    & ~filters.me
                    & filters.incoming
                ),
                "group": 3,
            },
            "CHATBOT": {
                "query": (
                    filters.mentioned & ~filters.bot & ~filters.me & filters.incoming
                ),
                "group": 4,
            },
            "REP_BLOCK": {
                "query": (
                    filters.mentioned
                    & ~filters.bot
                    & ~filters.me
                    & filters.incoming
                    & filters.create(is_blocked)
                ),
                "group": 5,
            },
            "REPLY": {
                "query": (filters.reply & filters.me),
                "group": 6,
            },
            "ADD_ME": {
                "query": (filters.new_chat_members),
                "group": 7,
            },
            "AUTO_APPROVE": {
                "query": (
                    filters.private
                    & filters.outgoing
                    & filters.me
                    & ~filters.bot
                    & ~filters.via_bot
                    & ~filters.service
                ),
                "group": 8,
            },
            "FORCE_DEL": {
                "query": ((filters.incoming | filters.group) & ~filters.me),
                "group": 9,
            },
        }
        result_query = query_mapping.get(result)

        def decorator(func):
            if result_query:

                async def wrapped_func(client, message):
                    await func(client, message)

                client.on_message(
                    result_query["query"], group=int(result_query["group"])
                )(wrapped_func)
                return wrapped_func
            else:
                return func

        return decorator

    @staticmethod
    def IS_LOG(func):
        async def function(client, message):
            logs = await dB.get_var(client.me.id, "GRUPLOG")
            if logs:
                if message.chat.id != int(logs):
                    return
            else:
                pass
            return await func(client, message)

        return function

    @staticmethod
    def SELLER_AND_GC(func):
        async def function(client, message):
            user = message.from_user
            reseller = await dB.get_list_from_var(BOT_ID, "SELLER")
            if user.id not in reseller:
                return await message.reply("<b>Kamu bukan reseller!!</b>")

            return await func(client, message)

        return function

    @staticmethod
    def DB_BROADCAST(func):
        async def function(client, message):
            broadcast = await dB.get_list_from_var(client.me.id, "BROADCAST")
            user = message.from_user
            if user.id not in broadcast:
                await dB.add_to_var(client.me.id, "BROADCAST", user.id)
            return await func(client, message)

        return function

    @staticmethod
    def ADMIN(func):
        async def function(client, message):
            emo = Emoji(client)
            await emo.get()
            user = message.from_user if message.from_user else message.sender_chat
            if user.id not in await client.admin_list(message):
                return await message.reply(
                    f"<b>{emo.gagal}Ensure youre admins in this chat.</b>"
                )
            return await func(client, message)

        return function

    @staticmethod
    def ONLY_GROUP(func):
        async def function(client, message):
            if message.chat.type not in [
                enums.ChatType.GROUP,
                enums.ChatType.SUPERGROUP,
            ]:
                emo = Emoji(client)
                await emo.get()
                return await message.reply(
                    f"{emo.gagal}<b>This command only for group.</b>"
                )
            return await func(client, message)

        return function

    @staticmethod
    def ONLY_PRIVATE(func):
        async def function(client, message):
            if message.chat.type != enums.ChatType.PRIVATE:
                emo = Emoji(client)
                await emo.get()
                return await message.reply(
                    f"{emo.gagal}<b>This command only for private.</b>"
                )
            return await func(client, message)

        return function

    @staticmethod
    def INLINE_QUERY(func):
        async def wrapper(client, iq):
            users = navy._get_my_id
            if iq.from_user.id not in users:
                return await client.answer_inline_query(
                    iq.id,
                    cache_time=0,
                    results=[
                        InlineQueryResultArticle(
                            title=f"Anda Belum Melakukan Pembelian @{client.me.username}",
                            input_message_content=InputTextMessageContent(
                                f"Kamu Bisa Melakukan Pembelian @{client.me.username} Agar Bisa Menggunakan"
                            ),
                        )
                    ],
                )
            else:

                return await func(client, iq)

        return wrapper

    @staticmethod
    def CALLBACK_DATA(func):
        async def wrapper(client, cq):
            users = navy._get_my_id
            if cq.from_user.id not in users:
                return await cq.answer(
                    f"Silakan Order Bot @{client.me.username} Agar Bisa Menggunakan Bot Ini",
                    True,
                )
            else:

                return await func(client, cq)

        return wrapper

