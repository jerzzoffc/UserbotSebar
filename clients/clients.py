import asyncio
import importlib
import os
import re
import shlex
import subprocess
import traceback
from datetime import datetime
from functools import wraps
from typing import Optional

from pyrogram import (Client, StopPropagation, enums, errors, filters, raw,
                      types)
from pyrogram.handlers import (CallbackQueryHandler, EditedMessageHandler,
                               MessageHandler)
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
from pytgcalls import PyTgCalls
from pytgcalls import filters as fl

from config import (AKSES_DEPLOY, API_HASH, API_ID, BOT_ID, BOT_NAME,
                    BOT_TOKEN, HELPABLE, IS_JASA_PRIVATE, LOG_BACKUP, OWNER_ID,
                    SUDO_OWNERS)
from database import dB
from logs import logger
from plugins import _PLUGINS

if not os.path.exists("downloads"):
    os.makedirs("downloads")


list_error = []


class BaseClient(Client):
    _ubot = []
    _prefix = {}
    _get_my_id = []
    _translate = {}
    _get_my_peer = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def get_privileges(self, chat_id: int, user_id: int):
        member = await self.get_chat_member(chat_id, user_id)
        privileges = member.privileges
        return privileges

    async def parse_topic(self, chat_id: int):
        data_forum = []
        title = (await self.get_chat(chat_id)).title
        async for topic in self.get_forum_topics(chat_id):
            data_forum.append({"id": topic.id, "title": topic.title})
        return title, data_forum

    async def get_call(self, chat_id: int) -> Optional[raw.types.InputGroupCall]:
        try:
            chat = await self.resolve_peer(chat_id)
        except (errors.PeerIdInvalid, errors.ChannelInvalid):
            return None

        if isinstance(chat, raw.types.InputPeerChannel):
            full_chat = await self.invoke(
                raw.functions.channels.GetFullChannel(
                    channel=raw.types.InputChannel(
                        channel_id=chat.channel_id, access_hash=chat.access_hash
                    )
                )
            )
        else:
            full_chat = await self.invoke(
                raw.functions.messages.GetFullChat(chat_id=chat_id)
            )

        input_call = full_chat.full_chat.call

        if input_call is not None:
            call_details = await self.invoke(
                raw.functions.phone.GetGroupCall(call=input_call, limit=-1)
            )
            call = call_details.call

            if call is not None and call.schedule_date is not None:
                return None

            return call

        return None

    async def admin_list(self, message):
        return [
            member.user.id
            async for member in message._client.get_chat_members(
                message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS
            )
        ]

    async def get_chat_id(self, query):
        chat_types = {
            "global": [
                enums.ChatType.CHANNEL,
                enums.ChatType.GROUP,
                enums.ChatType.SUPERGROUP,
            ],
            "all": [
                enums.ChatType.GROUP,
                enums.ChatType.SUPERGROUP,
                enums.ChatType.PRIVATE,
            ],
            "group": [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP],
            "bot": [enums.ChatType.BOT],
            "usbot": [enums.ChatType.PRIVATE, enums.ChatType.BOT],
            "private": [enums.ChatType.PRIVATE],
            "channel": [enums.ChatType.CHANNEL],
        }

        if query not in chat_types:
            return []

        valid_chat_types = chat_types[query]
        chat_ids = []

        try:
            async for dialog in self.get_dialogs():
                try:
                    chat = dialog.chat
                    if chat and chat.type in valid_chat_types:
                        chat_ids.append(chat.id)
                except Exception:
                    continue
        except Exception:
            pass

        return chat_ids

    def new_arg(self, message):
        if message.reply_to_message and len(message.command) < 3:
            msg = message.reply_to_message.text or message.reply_to_message.caption
            if not msg:
                return ""
            msg = msg.encode().decode("UTF-8")
            msg = msg.replace(" ", "", 2) if msg[2] == " " else msg
            return msg
        elif len(message.command) > 2:
            return " ".join(message.command[2:])
        else:
            return ""

    def extract_type_and_msg(self, message, is_reply_text=False):
        args = message.text.split(None, 2)

        if len(args) < 2:
            return None, None

        type = args[1]

        if is_reply_text:
            msg = (
                message.reply_to_message.text
                if message.reply_to_message
                else args[2] if len(args) > 2 else None
            )
        else:
            msg = (
                message.reply_to_message
                if message.reply_to_message
                else args[2] if len(args) > 2 else None
            )

        return type, msg

    async def get_translate(self):
        data = await dB.get_var(self.me.id, "_translate")
        if data:
            return data
        return "id"

    def get_message(self, message):
        if message.reply_to_message:
            return message.reply_to_message
        elif len(message.command) > 1:
            return " ".join(message.command[1:])
        return ""

    def get_name(self, message):
        if message.reply_to_message:
            if message.reply_to_message.sender_chat:
                return None
            first_name = message.reply_to_message.from_user.first_name or ""
            last_name = message.reply_to_message.from_user.last_name or ""
            full_name = f"{first_name} {last_name}".strip()
            return full_name if full_name else None
        else:
            input_text = message.text.split(None, 1)
            if len(input_text) <= 1:
                first_name = message.from_user.first_name or ""
                last_name = message.from_user.last_name or ""
                full_name = f"{first_name} {last_name}".strip()
                return full_name if full_name else None
            return input_text[1].strip()

    def get_arg(self, message):
        if message.reply_to_message and len(message.command) < 2:
            msg = message.reply_to_message.text or message.reply_to_message.caption
            if not msg:
                return ""
            msg = msg.encode().decode("UTF-8")
            msg = msg.replace(" ", "", 1) if msg[1] == " " else msg
            return msg
        elif len(message.command) > 1:
            return " ".join(message.command[1:])
        else:
            return ""

    def get_text(self, message):
        if message.reply_to_message:
            if len(message.command) < 2:
                text = (
                    message.reply_to_message.text
                    or message.reply_to_message.caption
                    or message.text.split(None, 1)[1]
                )
            else:
                text = (
                    (
                        message.reply_to_message.text
                        or message.reply_to_message.caption
                        or ""
                    )
                    + "\n\n"
                    + message.text.split(None, 1)[1]
                )
        else:
            if len(message.command) < 2:
                text = ""
            else:
                text = message.text.split(None, 1)[1]
        return text

    async def run_cmd(self, cmd):
        args = shlex.split(cmd)
        try:
            process = await asyncio.create_subprocess_exec(
                *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return (
                stdout.decode("utf-8", "replace").strip(),
                stderr.decode("utf-8", "replace").strip(),
                process.returncode,
                process.pid,
            )
        except NotImplementedError:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
            )
            stdout, stderr = process.communicate()
            return (
                stdout.decode("utf-8", "replace").strip(),
                stderr.decode("utf-8", "replace").strip(),
                process.returncode,
                process.pid,
            )

    async def extract_userid(self, message, text):
        def is_int(text):
            try:
                int(text)
            except ValueError:
                return False
            return True

        text = text.strip()

        if is_int(text):
            return int(text)

        try:
            entities = message.entities
            app = message._client
            entity = entities[1 if message.text.startswith("/") else 0]
            if entity.type == enums.MessageEntityType.MENTION:
                try:
                    return (await app.get_users(text)).id
                except (errors.UsernameNotOccupied, errors.UsernameInvalid):
                    return None
            if entity.type == enums.MessageEntityType.TEXT_MENTION:
                return entity.user.id
        except (AttributeError, IndexError, ValueError):
            return None

    async def extract_user_and_reason(self, message, sender_chat=False):
        args = message.text.strip().split()
        text = message.text
        user = None
        reason = None
        if message.reply_to_message:
            reply = message.reply_to_message
            if not reply.from_user:
                if (
                    reply.sender_chat
                    and reply.sender_chat != message.chat.id
                    and sender_chat
                ):
                    id_ = reply.sender_chat.id
                else:
                    return None, None
            else:
                id_ = reply.from_user.id

            if len(args) < 2:
                reason = None
            else:
                reason = text.split(None, 1)[1]
            return id_, reason

        if len(args) == 2:
            user = text.split(None, 1)[1]
            return await self.extract_userid(message, user), None

        if len(args) > 2:
            user, reason = text.split(None, 2)[1:]
            return await self.extract_userid(message, user), reason

        return user, reason

    async def extract_user(self, message):
        return (await self.extract_user_and_reason(message))[0]

    def set_prefix(self, user_id, prefix):
        self._prefix[self.me.id] = prefix

    def get_prefix(self, user_id):
        return self._prefix.get(user_id, [".", ",", "?", "+", "!"])


class UserBot(BaseClient):
    __module__ = "pyrogram.client"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_version = "18.01"
        self.device_model = BOT_NAME
        self.system_version = "KN-Devs"
        self.group_call = PyTgCalls(self)
        self.in_memory = True

    def on_message(self, filters=None, group=-1):
        def decorator(func):
            @wraps(func)
            async def wrapper(client, message):
                try:
                    if asyncio.iscoroutinefunction(func):
                        await func(client, message)
                    else:
                        func(client, message)
                except (errors.FloodWait, errors.FloodPremiumWait) as e:
                    logger.warning(f"FloodWait: Sleeping for {e.value} seconds.")
                    await asyncio.sleep(e.value)
                    await func(client, message)
                except (
                    errors.ChatWriteForbidden,
                    errors.ChatSendMediaForbidden,
                    errors.ChatSendPhotosForbidden,
                    errors.MessageNotModified,
                    errors.MessageIdInvalid,
                ):
                    pass
                except StopPropagation:
                    raise
                except Exception as e:
                    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    user_id = message.from_user.id if message.from_user else "Unknown"
                    chat_id = message.chat.id if message.chat else "Unknown"
                    chat_username = (
                        f"@{message.chat.username}"
                        if message.chat.username
                        else "Private Group"
                    )
                    command = message.text
                    error_trace = traceback.format_exc()
                    error_message = (
                        f"<b>Error:</b> {type(e).__name__}\n"
                        f"<b>Date:</b> {date_time}\n"
                        f"<b>Chat ID:</b> {chat_id}\n"
                        f"<b>Chat Username:</b> {chat_username}\n"
                        f"<b>User ID:</b> {user_id}\n"
                        f"<b>Command/Text:</b>\n<pre language='python'><code>{command}</code></pre>\n\n"
                        f"<b>Traceback:</b>\n<pre language='python'><code>{error_trace}</code></pre>"
                    )
                    await bot.send_message(LOG_BACKUP, error_message)

            handler = MessageHandler(wrapper, filters)
            for ub in self._ubot:
                ub.add_handler(handler, group)
            return func

        return decorator

    def on_edited_message(self, filters=None, group=-1):
        def decorator(func):
            for ub in self._ubot:
                ub.add_handler(EditedMessageHandler(func, filters), group)
            return func

        return decorator

    def group_call_logs(self):
        def decorator(func):
            for ub in self._ubot:
                ub.group_call.on_update(fl.stream_end)(func)
            return func

        return decorator

    def user_prefix(self, cmd):
        command_re = re.compile(r"([\"'])(.*?)(?<!\\)\1|(\S+)")

        async def func(_, client, message):
            if message.text:
                text = message.text.strip().encode("utf-8").decode("utf-8")
                username = client.me.username or ""
                prefixes = self.get_prefix(client.me.id)

                if not text:
                    return False

                for prefix in prefixes:
                    if not text.startswith(prefix):
                        continue

                    without_prefix = text[len(prefix) :]

                    for command in cmd.split("|"):
                        if not re.match(
                            rf"^(?:{command}(?:@?{username})?)(?:\s|$)",
                            without_prefix,
                            flags=re.IGNORECASE | re.UNICODE,
                        ):
                            continue

                        without_command = re.sub(
                            rf"{command}(?:@?{username})?\s?",
                            "",
                            without_prefix,
                            count=1,
                            flags=re.IGNORECASE | re.UNICODE,
                        )
                        message.command = [command] + [
                            re.sub(r"\\([\"'])", r"\1", m.group(2) or m.group(3) or "")
                            for m in command_re.finditer(without_command)
                        ]

                        return True

                return False

        return filters.create(func)

    async def start(self):
        await super().start()
        await self.group_call.start()
        self.group_call.cache_peer
        prefixes = await dB.get_pref(self.me.id)
        if prefixes:
            self._prefix[self.me.id] = prefixes
        else:
            self._prefix[self.me.id] = [".", ",", "?", "+", "!"]
        self._ubot.append(self)
        self._get_my_id.append(self.me.id)
        # logger.info(f"Starting Userbot {self.me.id}|@{self.me.username}")

    async def stop(self, *args, **kwargs):
        await super().stop(*args, **kwargs)


class Bot(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(
            name="Bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            device_model=BOT_NAME,
            plugins={"root": "assistant"},
            in_memory=True,
            **kwargs,
        )

    def on_message(self, filters=None, group=-1):
        def decorator(func):
            @wraps(func)
            async def wrapper(client, message):
                try:
                    if asyncio.iscoroutinefunction(func):
                        await func(client, message)
                    else:
                        func(client, message)
                except (errors.FloodWait, errors.FloodPremiumWait) as e:
                    logger.warning(f"FloodWait: Sleeping for {e.value} seconds.")
                    await asyncio.sleep(e.value)
                    await func(client, message)
                except (
                    errors.ChatWriteForbidden,
                    errors.ChatSendMediaForbidden,
                    errors.ChatSendPhotosForbidden,
                    errors.MessageNotModified,
                    errors.MessageIdInvalid,
                ):
                    pass
                except StopPropagation:
                    raise
                except Exception as e:
                    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    user_id = message.from_user.id if message.from_user else "Unknown"
                    chat_id = message.chat.id if message.chat else "Unknown"
                    chat_username = (
                        f"@{message.chat.username}"
                        if message.chat.username
                        else "Private Group"
                    )
                    command = message.text
                    error_trace = traceback.format_exc()
                    error_message = (
                        f"<b>Error:</b> {type(e).__name__}\n"
                        f"<b>Date:</b> {date_time}\n"
                        f"<b>Chat ID:</b> {chat_id}\n"
                        f"<b>Chat Username:</b> {chat_username}\n"
                        f"<b>User ID:</b> {user_id}\n"
                        f"<b>Command/Text:</b>\n<pre language='python'><code>{command}</code></pre>\n\n"
                        f"<b>Traceback:</b>\n<pre language='python'><code>{error_trace}</code></pre>"
                    )
                    await bot.send_message(LOG_BACKUP, error_message)

            handler = MessageHandler(wrapper, filters)
            self.add_handler(handler, group)
            return func

        return decorator

    def on_callback_query(self, filters=None, group=-1):
        def decorator(function):
            self.add_handler(CallbackQueryHandler(function, filters), group)
            return function

        return decorator

    async def add_reseller(self):
        for user in SUDO_OWNERS:
            if user not in await dB.get_list_from_var(BOT_ID, "SELLER"):
                await dB.add_to_var(BOT_ID, "SELLER", user)
        if OWNER_ID not in await dB.get_list_from_var(BOT_ID, "SELLER"):
            await dB.add_to_var(BOT_ID, "SELLER", OWNER_ID)
        for user in await dB.get_list_from_var(BOT_ID, "SELLER"):
            if user not in AKSES_DEPLOY:
                AKSES_DEPLOY.append(user)
        for u in await dB.get_list_from_var(BOT_ID, "SELLER"):
            if not await dB.get_var(u, "plan"):
                await dB.set_var(u, "plan", "is_pro")

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.fullname = f"{self.me.first_name} {self.me.last_name or ''}"
        self.username = self.me.username
        self.mention = self.me.mention
        user_cmd = [
            types.BotCommand("start", "Start the bot."),
            types.BotCommand("bug", "Report a bug."),
            types.BotCommand("request", "Feature request."),
            types.BotCommand("restart", "Restart your userbot."),
        ]
        await self.set_bot_commands(
            user_cmd, scope=types.BotCommandScopeAllPrivateChats()
        )
        if IS_JASA_PRIVATE:
            owner_cmd = [
                types.BotCommand("addprem", "Berikan akses deploy."),
                types.BotCommand("addseller", "Berikan akses seller."),
                types.BotCommand("unseller", "Hapus akses seller."),
                types.BotCommand("listseller", "Cek daftar seller."),
                types.BotCommand("cekubot", "Lihat pengguna bot."),
            ]
            await self.set_bot_commands(
                user_cmd + owner_cmd,
                scope=types.BotCommandScopeChat(chat_id=OWNER_ID),
            )
        for modul in _PLUGINS:
            imported_module = importlib.import_module(f"plugins.{modul}")
            is_pro_plugin = getattr(imported_module, "IS_PRO", False)
            is_basic_plugin = getattr(imported_module, "IS_BASIC", False)
            module_name = getattr(imported_module, "__MODULES__", "").lower()
            if module_name:
                HELPABLE[module_name] = {
                    "module": imported_module,
                    "is_pro": is_pro_plugin,
                    "is_basic": is_basic_plugin,
                }
        logger.info(f"🔥 {self.username} Bot Started 🔥")


navy = UserBot(name="clients")
bot = Bot()

