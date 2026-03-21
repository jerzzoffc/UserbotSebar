import traceback

import config
from helpers import Emoji, Tools, animate_proses
from logs import logger

GEMINI_CHAT_URL = "https://api.maelyn.sbs/api/gemini/chat"
GEMINI_IMAGE_URL = "https://api.maelyn.sbs/api/gemini/image"
GEMINI_VIDEO_URL = "https://api.maelyn.sbs/api/gemini/video"


async def gemini_cmd(client, message):
    em = Emoji(client)
    await em.get()
    proses = await animate_proses(message, em.proses)

    if len(message.command) < 2:
        return await proses.edit(
            f"{em.gagal}**Please give a question or reply with an image and question.**"
        )
    prompt = message.text.split(None, 1)[1]
    try:
        headers = {"mg-apikey": config.API_MAELYN}

        if message.reply_to_message and message.reply_to_message.photo:
            if len(message.command) < 2:
                return await proses.edit(
                    f"{em.gagal}**Please provide a question to analyze the image.**"
                )
            photo_url = await Tools.maelyn_upload(message)

            params = {"url": photo_url, "q": prompt}
            r = await Tools.fetch.get(GEMINI_IMAGE_URL, headers=headers, params=params)
            if r.status_code != 200:
                return await proses.edit(
                    f"<b>Please try again later: {r.status_code}</b>"
                )
            data = r.json()
            return await proses.edit(data.get("result"))
        elif message.reply_to_message and (
            message.reply_to_message.video,
            message.reply_to_message.animation,
        ):
            if len(message.command) < 2:
                return await proses.edit(
                    f"{em.gagal}**Please provide a question to analyze the image.**"
                )
            video_url = await Tools.maelyn_upload(message)

            params = {"url": video_url, "q": prompt}
            r = await Tools.fetch.get(GEMINI_VIDEO_URL, headers=headers, params=params)
            if r.status_code != 200:
                return await proses.edit(
                    f"<b>Please try again later: {r.status_code}</b>"
                )
            data = r.json()
            return await proses.edit(data.get("result"))

        else:
            params = {"q": prompt}
            r = await Tools.fetch.get(GEMINI_CHAT_URL, headers=headers, params=params)
            if r.status_code != 200:
                return await proses.edit(
                    f"<b>Please try again later: {r.status_code}</b>"
                )
            data = r.json()
            return await proses.edit(data.get("result"))

    except Exception as e:
        logger.error(traceback.format_exc())
        return await proses.edit(f"{em.gagal}**Terjadi kesalahan:**\n`{e}`")
