import random
import traceback

from pyrogram import enums, types
from pyrogram.errors import (AboutTooLong, PeerIdInvalid, UsernameInvalid,
                             UsernameNotOccupied)

from config import DEVS
from database import dB
from helpers import Emoji, Tools, animate_proses

angka = random.randint(1, 9)


async def update_profile(client, object, restore=False):
    if restore:
        memory = await dB.get_var(client.me.id, "CLONED")
        photos = memory.get("photo")
        del_photo = [p async for p in client.get_chat_photos("me")]
        await client.delete_profile_photos([p.file_id for p in del_photo])
        await client.update_profile(
            first_name=memory.get("first_name"),
            last_name=memory.get("last_name"),
            bio=memory.get("bio"),
        )
        if memory.get("premium") == True:
            emoji_status = memory.get("emoji_status")
            await client.set_emoji_status(
                types.EmojiStatus(custom_emoji_id=int(emoji_status))
            )
            reply_color_id = memory.get("reply_color")
            color_reply = memory.get("color_reply")
            if reply_color_id and color_reply:
                try:
                    reply_color_enum = enums.ReplyColor[color_reply]
                    await client.update_color(
                        chat_id="me",
                        color=reply_color_enum,
                        background_emoji_id=int(reply_color_id),
                    )
                except KeyError:
                    pass

            profile_color_id = memory.get("profile_color")
            color_profile = memory.get("color_profile")
            if profile_color_id and color_profile:
                try:
                    profile_color_enum = enums.ProfileColor[color_profile]
                    await client.update_color(
                        chat_id="me",
                        color=profile_color_enum,
                        background_emoji_id=int(profile_color_id),
                    )
                except KeyError:
                    pass

        if photos:
            media = f"downloads/{client.me.id}.jpg"
            await Tools.bash(f"wget {photos} -O {media}")
            try:
                await client.set_profile_photo(photo=media)
            except Exception:
                print(f"Error: {traceback.format_exc()}")
        await dB.remove_var(client.me.id, "CLONED")
        return

    object_premium = object.is_premium
    object_first_name = object.first_name
    object_last_name = object.last_name or ""
    object.username or ""
    bio = (await client.get_chat(object.id)).bio
    if bio is not None:
        object_bio = bio if object_premium else bio[:70]
    else:
        object_bio = ""
    if object_premium:
        try:
            object_emoji_status = (
                object.emoji_status.custom_emoji_id if object.emoji_status else None
            )

            reply_color_id = None
            profile_color_id = None
            object_reply_color = None
            object_profile_color = None

            if object.reply_color:
                object_reply_color = object.reply_color.color.name
                reply_color_id = object.reply_color.background_emoji_id

            if object.profile_color:
                object_profile_color = object.profile_color.color.name
                profile_color_id = object.profile_color.background_emoji_id

            if object_emoji_status:
                await client.set_emoji_status(
                    types.EmojiStatus(custom_emoji_id=object_emoji_status)
                )

            if reply_color_id is not None and object_reply_color is not None:
                reply_color_enum = enums.ReplyColor[object_reply_color]
                await client.update_color(
                    chat_id="me",
                    color=reply_color_enum,
                    background_emoji_id=int(reply_color_id),
                )

            if profile_color_id is not None and object_profile_color is not None:
                profile_color_enum = enums.ProfileColor[object_profile_color]
                await client.update_color(
                    chat_id="me",
                    color=profile_color_enum,
                    background_emoji_id=int(profile_color_id),
                )
        except Exception:
            pass

    object_photos = [p async for p in client.get_chat_photos(object.id)]
    if object_photos:
        del_photo = [p async for p in client.get_chat_photos("me")]
        await client.delete_profile_photos([p.file_id for p in del_photo])
        # kwargs = {"photo": pfp} if pfp.startswith("AgAC") else {"video": pfp}
        pfp = await client.download_media(object_photos[0].file_id)
        try:
            await client.set_profile_photo(photo=pfp)
        except Exception:
            print(f"Error: {traceback.format_exc()}")
    try:
        await client.update_profile(
            first_name=object_first_name, last_name=object_last_name, bio=object_bio
        )
    except AboutTooLong:
        bio = (await client.get_chat(object.id)).bio
        if bio is not None:
            object_bio = bio[:70]
        else:
            object_bio = ""
        await client.update_profile(
            first_name=object_first_name, last_name=object_last_name, bio=object_bio
        )


async def clone_cmd(client, message):
    em = Emoji(client)
    await em.get()
    proses = await animate_proses(message, em.proses)
    reply = message.reply_to_message
    text_parts = message.text.split()
    if len(text_parts) > 1 and text_parts[1].lower() == "restore":
        if not await dB.get_var(client.me.id, "CLONED"):
            return await proses.edit(f"{em.gagal}**Please clone someone first!!**")
        await update_profile(client, client, restore=True)
        return await proses.edit(f"{em.sukses}**Profile rollback.**")
    if reply and reply.sender_chat:
        return await proses.edit(
            f"{em.gagal}**Please reply to user idiot, not anonymous account memek!!**"
        )
    try:
        target = reply.from_user.id if reply else text_parts[1]
    except (AttributeError, IndexError):
        return await proses.edit(
            f"{em.gagal}<b>You need to specify a user (either by reply or username/ID)!</b>"
        )
    try:
        user = await client.get_users(target)
    except (PeerIdInvalid, KeyError, UsernameInvalid, UsernameNotOccupied):
        return await proses.edit(f"{em.gagal}<b>You need meet before interact!!</b>")
    user_id = user.id
    if user_id in DEVS:
        return await proses.edit(f"{em.gagal}<b>Go to the heal now!!</b>")
    if not await dB.get_var(client.me.id, "CLONED"):
        me = client.me
        try:
            photos_me = [p async for p in client.get_chat_photos("me")]
            media = await client.download_media(photos_me[0].file_id)
            foto = await Tools.upload_thumb(media)
        except Exception:
            foto = ""
        data = {
            "premium": me.is_premium,
            "emoji_status": me.emoji_status.custom_emoji_id if me.is_premium else "",
            "first_name": me.first_name,
            "last_name": me.last_name or "",
            "username": me.username or "",
            "bio": (await client.get_chat("me")).bio or "",
            "reply_color": (
                getattr(me.reply_color, "background_emoji_id", "")
                if me.is_premium
                else ""
            ),
            "color_reply": (
                getattr(getattr(me.reply_color, "color", None), "name", "")
                if me.is_premium
                else ""
            ),
            "profile_color": (
                getattr(me.profile_color, "background_emoji_id", "")
                if me.is_premium
                else ""
            ),
            "color_profile": (
                getattr(getattr(me.profile_color, "color", None), "name", "")
                if me.is_premium
                else ""
            ),
            "photo": foto,
        }
        await dB.set_var(client.me.id, "CLONED", data)
    await update_profile(client, user)
    return await proses.edit(f"{em.sukses}**Profile updated.**")
