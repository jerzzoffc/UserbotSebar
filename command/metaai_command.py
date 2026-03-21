import traceback
from uuid import uuid4

from pyrogram.types import InputMediaAnimation, InputMediaPhoto

import config
from helpers import Emoji, Tools, animate_proses
from logs import logger

from .sosmed_command import chunk_media_group

META_AI_CHAT_URL = "https://api.maelyn.sbs/api/metaai/chat"
META_AI_IMAGINE_URL = "https://api.maelyn.sbs/api/metaai/art"


async def metaai_cmd(client, message):
    em = Emoji(client)
    await em.get()
    proses = await animate_proses(message, em.proses)

    if len(message.command) < 2:
        return await proses.edit(f"{em.gagal}**Please give a prompt or question.**")

    prompt = client.get_text(message)

    try:
        foto, video = 0, 0
        err = ""
        headers = {"mg-apikey": config.API_MAELYN}

        if prompt.lower().startswith("generate "):
            if len(message.command) < 3:
                return await proses.edit(
                    f"{em.gagal}**Please reply to a message prompt or give the prompt!\nExample: `{message.text.split()[0]} cute cats`**"
                )
            prompt = prompt[9:].strip()
            params = {"prompt": prompt}
            r = await Tools.fetch.get(
                META_AI_IMAGINE_URL, headers=headers, params=params
            )
            data = r.json()
            results = data.get("result", [])

            if not results:
                return await proses.edit(f"{em.gagal}**No media found.**")

            await proses.edit(f"{em.proses}**Preparing media for sending...**")

            photo_group = []
            video_group = []

            for item in results:
                photo_url = item.get("ImageUrl")
                video_url = item.get("VideoUrl")

                if photo_url:
                    _photo = await Tools.get_media_data(photo_url, "jpg")
                    if _photo and _photo.getbuffer().nbytes > 0:
                        _photo.name = f"{uuid4()}.jpg"
                        photo_group.append(InputMediaPhoto(media=_photo))
                        foto += 1

                if video_url:
                    _video = await Tools.get_media_data(video_url, "mp4")
                    if _video and _video.getbuffer().nbytes > 0:
                        _video.name = f"{uuid4()}.mp4"
                        video_group.append(InputMediaAnimation(media=_video))
                        video += 1

            await proses.delete()
            if photo_group:
                photo_chunks = chunk_media_group(photo_group)
                for i, chunk in enumerate(photo_chunks, 1):
                    try:
                        await client.send_media_group(
                            chat_id=message.chat.id, media=chunk
                        )
                    except Exception as e:
                        err += f"Error sending photo chunk {i}: {str(e)}\n"
            if video_group:
                for i, animation in enumerate(video_group, 1):
                    try:
                        await client.send_animation(
                            chat_id=message.chat.id,
                            animation=animation.media,
                        )
                    except Exception as e:
                        err += f"Error sending video {i}: {str(e)}\n"

            if not photo_group and not video_group:
                return await message.reply(f"{em.gagal}**No media found.**")

            return await message.reply(
                f"{em.sukses}**Successfully sent {foto + video} media**\n📸 Photos: `{foto}` | 🎥 Videos: `{video}`\n{err}"
            )

        else:
            params = {"q": prompt}
            r = await Tools.fetch.get(META_AI_CHAT_URL, headers=headers, params=params)
            data = r.json()
            return await proses.edit(data.get("result"))

    except Exception as e:
        logger.error(traceback.format_exc())
        return await proses.edit(f"{em.gagal}**Terjadi kesalahan:**\n`{e}`")
