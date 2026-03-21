import asyncio
import time
import traceback
from collections import defaultdict

from pyrogram import enums, errors

from clients import bot
from database import dB, state

from .buttons import ButtonUtils
from .emoji_logs import Emoji
from .message import Message
from .tools import Tools

afk_spam_tracker = defaultdict(list)
afk_last_sent_time = {}


class AFK_:
    @staticmethod
    async def set_afk(client, message):
        emo = Emoji(client)
        await emo.get()
        try:
            rep = message.reply_to_message
            if not rep and len(message.command) > 1:
                if len(message.command) < 3:
                    return await message.reply(
                        f"{emo.gagal}**Usage: `{message.text.split()[0]} mode` (private/all)**"
                    )
                if message.command[1] != "mode":
                    return await message.reply(
                        f"{emo.gagal}**Usage: `{message.text.split()[0]} mode` (private/all)**"
                    )
                if message.command[2] not in ["private", "all"]:
                    return await message.reply(
                        f"{emo.gagal}**Usage: `{message.text.split()[0]} mode` (private/all)**"
                    )
                _, mode, type = message.command[:3]
                if type == "private":
                    await dB.set_var(client.me.id, "mode", type)
                    return await message.reply(
                        f"{emo.sukses}**AFk {mode} set to: `{type}`.**"
                    )
                elif type == "all":
                    await dB.remove_var(client.me.id, mode)
                    return await message.reply(
                        f"{emo.sukses}**AFk {mode} set to: `{type}`.**"
                    )
                else:
                    return await message.reply(
                        f"{emo.gagal}<b>Please reply to message!!</b>"
                    )
            text = rep.text or rep.caption or ""
            entities = rep.entities or rep.caption_entities
            if rep.media and rep.media != enums.MessageMediaType.WEB_PAGE_PREVIEW:
                copy = await rep.copy(bot.me.username)
                sent = await client.send_message(
                    bot.me.username, f"/id afk", reply_to_message_id=copy.id
                )
                await asyncio.sleep(1)
                await sent.delete()
                await copy.delete()
                extract = Tools.dump_entity(text, entities)
                type = state.get(client.me.id, "afk")
                value = {
                    "type": type["type"],
                    "file_id": type["file_id"],
                    "result": extract,
                }
            else:
                extract = Tools.dump_entity(text, entities)
                value = {"type": "text", "file_id": "", "result": extract}
            if value:
                await dB.set_var(client.me.id, "AFK", value)

            return await message.reply(
                f"{emo.sukses}**AFK status set to: [this]({rep.link})"
            )
        except Exception as er:
            print(f"ERROR Setafk: {traceback.format_exc()}")
            return await message.reply(f"{emo.gagal}**ERROR**: `{str(er)}`")

    @staticmethod
    async def get_afk(client, message):
        emo = Emoji(client)
        await emo.get()

        try:
            data = await dB.get_var(client.me.id, "AFK")
            if not data:
                return
            now = time.time()
            chat_id = message.chat.id
            last_sent = afk_last_sent_time.get(chat_id)

            type = data["type"]
            file_id = data["file_id"]
            one, button = ButtonUtils.parse_msg_buttons(data["result"].get("text"))
            last_msg_id = await dB.get_var(message.chat.id, "afk_last_message")
            if last_sent and now - last_sent < 600:
                return
            afk_last_sent_time[chat_id] = now
            if last_msg_id:
                try:
                    await client.delete_messages(message.chat.id, last_msg_id)
                    await dB.remove_var(message.chat.id, "afk_last_message")
                except Exception:
                    pass

            state.set(client.me.id, "afk", id(message))
            only_private = await dB.get_var(client.me.id, "mode")
            if only_private:
                if message.chat.type != enums.ChatType.PRIVATE:
                    return

            if button:
                try:
                    await ButtonUtils.send_inline_bot_result(
                        message,
                        message.chat.id,
                        bot.me.username,
                        "inline_afk",
                        reply_to_message_id=Message.ReplyCheck(message),
                    )
                    chat_id = state.get("inline_afk", "inline_afk").get("chat")
                    message_id = state.get("inline_afk", "inline_afk").get("_id")
                    await dB.set_var(chat_id, "afk_last_message", message_id)
                    return
                except errors.SlowmodeWait as e:
                    await asyncio.sleep(e.value)
                    await ButtonUtils.send_inline_bot_result(
                        message,
                        message.chat.id,
                        bot.me.username,
                        "inline_afk",
                        reply_to_message_id=Message.ReplyCheck(message),
                    )
                    chat_id = state.get("inline_afk", "inline_afk").get("chat")
                    message_id = state.get("inline_afk", "inline_afk").get("_id")
                    await dB.set_var(chat_id, "afk_last_message", message_id)
                    return
                except errors.RPCError:
                    pass
            teks = await Tools.escape_filter(message, one, Tools.parse_words)
            if type == "text":
                try:
                    sent = await message.reply(
                        teks,
                        parse_mode=enums.ParseMode.HTML,
                        reply_to_message_id=message.id,
                    )
                except errors.ChatWriteForbidden:
                    return
            else:
                senders = {
                    "photo": message.reply_photo,
                    "voice": message.reply_voice,
                    "audio": message.reply_audio,
                    "video": message.reply_video,
                    "animation": message.reply_animation,
                    "document": message.reply_document,
                    "sticker": message.reply_sticker,
                    "video_note": message.reply_video_note,
                }

                try:
                    didel = await getattr(bot, f"send_{type}")(client.me.id, file_id)
                    async for m in client.search_messages(bot.username, limit=1):
                        media_obj = getattr(m, type, None)
                        new_fileid = (
                            getattr(media_obj, "file_id", None) if media_obj else None
                        )
                        break
                    else:
                        return await message.reply("**AFK: File not found.**")

                    kwargs = {"reply_to_message_id": message.id}
                    if type not in ["sticker", "video_note"]:
                        kwargs["caption"] = teks
                        kwargs["parse_mode"] = enums.ParseMode.HTML
                    try:
                        sent = await senders[type](new_fileid, **kwargs)
                    except Exception:
                        sent = await message.reply(
                            teks,
                            parse_mode=enums.ParseMode.HTML,
                            reply_to_message_id=message.id,
                        )
                    except errors.ChatWriteForbidden:
                        return
                    await bot.delete_messages(bot.username, didel.id)

                except Exception:
                    return await message.reply(
                        f"**AFK send error:** `{traceback.format_exc()}`"
                    )

            await dB.set_var(message.chat.id, "afk_last_message", sent.id)

        except Exception:
            print(f"AFK ERROR:\n{traceback.format_exc()}")
            return

    @staticmethod
    async def unset_afk(client, message):
        emo = Emoji(client)
        await emo.get()
        vars = await dB.get_var(client.me.id, "AFK")
        if vars:
            afk_text = f"<b>{emo.sukses}Back to Online!!</b>"
            last_message = await dB.get_var(message.chat.id, "afk_last_message")
            if last_message:
                try:
                    await client.delete_messages(message.chat.id, last_message)
                    await dB.remove_var(message.chat.id, "afk_last_message")
                except Exception:
                    pass
            await dB.remove_var(client.me.id, "AFK")
            ae = await message.reply(afk_text)
            async for m in client.get_chat_history(message.chat.id):
                if m.reply_markup:
                    await m.delete()
            return await ae.delete()
