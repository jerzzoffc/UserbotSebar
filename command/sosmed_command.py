import os
import time
import traceback
from datetime import timedelta
from itertools import islice
from typing import List
from uuid import uuid4

import wget
from pyrogram import enums
from pyrogram.errors import ChatForwardsRestricted
from pyrogram.types import InputMediaAudio, InputMediaPhoto, InputMediaVideo

from clients import bot
from config import API_MAELYN
from database import state
from helpers import (ButtonUtils, Emoji, Spotify, Tools, YoutubeSearch,
                     animate_proses, youtube)
from logs import logger


def chunk_media_group(media_list: list, chunk_size: int = 4) -> List[list]:
    """Split media list into chunks of specified size"""
    media_chunks = []
    iterator = iter(media_list)
    while chunk := list(islice(iterator, chunk_size)):
        media_chunks.append(chunk)
    return media_chunks


async def spotdl_cmd(client, message, proses, arg):
    em = Emoji(client)
    await em.get()
    await proses.edit(f"{em.proses}**Wait a minute this takes some time...**")
    if arg.split("/")[-2] != "track":
        return await proses.edit(
            f"{em.gagal}**Sorry only track supported!!**\n**Example:** https://open.spotify.com/track/0pmyq5KBXP3agRdxl1SZXx?si=3k3nnok6QtCkMF-XRzBo5w",
            disable_web_page_preview=True,
        )
    now = time.time()
    url = await Spotify.track(arg)
    (
        file_path,
        info,
        title,
        duration,
        views,
        channel,
        url,
        _,
        thumb,
        data_ytp,
    ) = await youtube.download(url.get("file_path"), as_video=False)
    thumbnail = wget.download(thumb)
    caption = data_ytp.format(
        info, title, timedelta(seconds=duration), views, channel, url, client.me.mention
    )
    try:
        await message.reply_audio(
            audio=file_path,
            title=title,
            thumb=thumbnail,
            performer=channel,
            duration=duration,
            caption=caption,
            progress=youtube.progress,
            progress_args=(proses, now, f"<b>Sending request...</b>", f"{title}"),
        )
        return await proses.delete()
    except Exception:
        logger.error(f"Eror download spotify: {traceback.format_exc()}")
        return await proses.edit(f"{em.gagal}**ERROR Please contact developer.*")


async def ytvideo_cmd(client, message, proses, arg):
    try:
        emo = Emoji(client)
        await emo.get()
        await proses.edit(f"{emo.proses}**Wait a minute this takes some time...**")
        now = time.time()
        try:
            yt_search = YoutubeSearch(arg, max_results=1)
            await yt_search.fetch_results()
            link = yt_search.get_link()
            if link is None:
                link = arg
            else:
                link = link
            logger.info(f"Link: {link}")
        except Exception as error:
            return await proses.edit(
                f"{emo.gagal}<b>ERROR:</b><code>{str(error)}</code>"
            )
        try:
            (
                file_name,
                inpoh,
                title,
                duration,
                views,
                channel,
                url,
                _,
                thumb,
                data_ytp,
            ) = await youtube.download(link, as_video=True)

            if isinstance(duration, str):
                duration = duration.replace(".", "")
            duration = int(duration)

        except Exception as error:
            return await proses.edit(
                f"{emo.gagal}<b>ERROR:</b><code>{str(error)}</code>"
            )

        thumbnail = wget.download(thumb)
        kapten = data_ytp.format(
            inpoh,
            title,
            timedelta(seconds=duration),
            views,
            channel,
            url,
            bot.me.mention,
        )
        await client.send_video(
            message.chat.id,
            video=file_name,
            thumb=thumbnail,
            file_name=title,
            duration=duration,
            supports_streaming=True,
            caption=f"{kapten}",
            progress=youtube.progress,
            progress_args=(
                proses,
                now,
                f"{emo.proses}<b>Trying to upload...</b>",
                f"{file_name}",
            ),
            reply_to_message_id=message.id,
        )
        await proses.delete()
        if os.path.exists(thumbnail):
            os.remove(thumbnail)
        if os.path.exists(file_name):
            os.remove(file_name)
    except Exception as er:
        logger.error(f"Error: {traceback.format_exc()}")


async def teledl_cmd(client, message, proses, link):
    em = Emoji(client)
    await em.get()
    chat_id = message.chat.id
    await proses.edit(f"{em.proses}**Wait a minute this takes some time...**")
    logger.info(f"Chat ID: {chat_id}\nLink: {link}")
    if link.startswith(("https", "t.me")):
        if link.endswith("?single"):
            links = link.replace("?single", "")
            logger.info(f"Link Single: {links}")
            parts = links.split("/")
            if len(parts) == 7:
                chat = f"-100{parts[4]}"
                msg_id = int(parts[6])
            else:
                chat = parts[3]
                msg_id = int(parts[4])
            logger.info(f"Chat Single: {chat}")
            logger.info(f"Message ID Single: {msg_id}")
            try:
                await client.copy_media_group(message.chat.id, chat, msg_id)
                return await proses.delete()
            except Exception as e:
                logger.info(f"Chat Single: {chat}")
                logger.info(f"Message ID Single: {msg_id}")
                media_group = []
                mediaa = await client.get_messages(int(chat), int(msg_id))
                medias = await mediaa.get_media_group()
                for msg in medias:
                    if msg.photo:
                        media_group.append(
                            InputMediaPhoto(
                                media=await client.download_media(msg.photo.file_id),
                                caption=msg.caption,
                            )
                        )
                    elif msg.video:
                        media_group.append(
                            InputMediaVideo(
                                media=await client.download_media(msg.video.file_id),
                                caption=msg.caption,
                            )
                        )
                    else:
                        print(f"Skipping message {msg.id}: no media found.")
                if media_group:
                    await client.send_media_group(message.chat.id, media_group)
                    return await proses.delete()

                return await proses.edit(
                    f"><b>{em.gagal} Failed to Copy Message from {chat} {msg_id}: {e}</b>"
                )
        if "?single" in link:
            link = link.replace("?single", "")
        if "/s/" in link:
            user, story_id = Tools.extract_story_link(link)
            story = await client.get_stories(user, story_id)
            await Tools.download_media(story, client, proses, message, True)
            return await proses.delete()
        if "?comment=" in link:
            link_parts = link.split("?comment=")
            msg_id = int(link_parts[0].split("/")[-1])
            tlinket = int(link_parts[1].split("/")[-1])
            chid = str(link.split("/")[-2])
            chat = await client.get_discussion_message(chid, msg_id)
            try:
                get_msg = await client.get_messages(chat.chat.id, tlinket)
                try:
                    await get_msg.copy(chat_id)
                    return await proses.delete()
                except ChatForwardsRestricted:
                    return await Tools.download_media(get_msg, client, proses, message)
            except Exception as e:
                return await proses.edit(str(e))
        if "t.me/c/" in link:
            parts = link.split("/")
            if len(parts) == 7:
                chat = f"-100{parts[4]}"
                msg_id = int(parts[6])
            else:
                chat = f"-100{parts[4]}"
                msg_id = int(parts[5])
            logger.info(f"Chat: {chat}")
            logger.info(f"Msg ID: {msg_id}")
            try:
                get_msg = await client.get_messages(chat, msg_id)
                try:
                    await get_msg.copy(chat_id)
                    return await proses.delete()
                except ChatForwardsRestricted:
                    return await Tools.download_media(get_msg, client, proses, message)
            except Exception as e:
                return await proses.edit(str(e))
        else:
            msg_id = int(link.split("/")[-1])
            get_chat = str(link.split("/")[-2])
            try:
                chat = await client.get_chat(get_chat)
                get_msg = await client.get_messages(chat.id, msg_id)
                await get_msg.copy(chat_id)
                return await proses.delete()
            except ChatForwardsRestricted:
                return await Tools.download_media(get_msg, client, proses, message)
            except Exception as e:
                return await proses.edit(str(e))

    else:
        return await proses.edit(f"{em.gagal}<b>Please give valid link!!</b>")


async def instadl_cmd(client, message, proses, arg):
    em = Emoji(client)
    await em.get()
    await proses.edit(f"{em.proses}**Wait a minute this takes some time...**")
    err = ""
    foto, video = 0, 0

    try:
        url = f"https://api.maelyn.sbs/api/instagram?url={arg}&apikey={API_MAELYN}"
        response = await Tools.fetch.get(url)

        if response.status_code != 200:
            return await proses.edit(
                f"{em.gagal}**Request failed with status code {response.status_code}**"
            )

        data = response.json()
        results = data.get("result", [])

        if not results:
            return await proses.edit(
                f"{em.gagal}**No media found in the instagram links**"
            )

        await proses.edit(f"{em.proses}**Preparing media for sending...**")
        media_group = []

        for item in results:
            download_url = item.get("download_link")
            if not download_url:
                continue
            media_type = await Tools.get_media_type(download_url)
            if media_type == "photo":
                media = await Tools.get_media_data(download_url, "jpg")
                media_group.append(InputMediaPhoto(media=media))
                foto += 1
            else:
                media = await Tools.get_media_data(download_url, "mp4")
                media_group.append(InputMediaVideo(media=media))
                video += 1

        if not media_group:
            return await proses.edit(
                f"{em.gagal}**Failed to prepare any media for sending.**"
            )

        media_chunks = chunk_media_group(media_group)
        await proses.delete()

        for i, chunk in enumerate(media_chunks, 1):
            try:
                await client.send_media_group(chat_id=message.chat.id, media=chunk)
            except Exception as chunk_error:
                err += f"Error sending chunk {i}: {str(chunk_error)}\n"

        return await message.reply(
            f"{em.sukses}**Successfully sent {len(media_group)} media\n📸 Photos: `{foto}` | 🎥 Videos: `{video}`**\n{err}"
        )

    except Exception as er:
        logger.error(f"instadl: {traceback.format_exc()}")
        return await message.reply(f"{em.gagal}**ERROR:** {str(er)}")


async def ttdl_cmd(client, message, proses, arg):
    em = Emoji(client)
    await em.get()
    await proses.edit(f"{em.proses}**Wait a minute this takes some time...**")
    url = f"https://api.maelyn.sbs/api/tiktok/download?url={arg}&apikey={API_MAELYN}"

    foto, video, audio = 0, 0, 0
    err = ""
    media_group = []
    audio_group = []
    try:
        response = await Tools.fetch.get(url)
        if response.status_code != 200:
            return await proses.edit(
                f"{em.gagal}**Request failed with status code {response.status_code}**"
            )

        data = response.json()
        if not data.get("result"):
            return await proses.edit(f"{em.gagal}**No media found in response**")

        await proses.edit(f"{em.proses}**Preparing media for sending...**")

        if data["result"].get("video"):
            result_video = data["result"]["video"]
            url_video = result_video["nwm_url_hq"]
            media_data = await Tools.get_media_data(url_video, "mp4")
            media_group.append(InputMediaVideo(media=media_data))
            video += 1
        if data["result"].get("image_data"):
            result_photo = data["result"]["image_data"]
            url_photo = result_photo["no_watermark_image_list"]
            for uri in url_photo:
                media_data = await Tools.get_media_data(uri, "jpg")
                media_group.append(InputMediaPhoto(media=media_data))
                foto += 1
        if data["result"].get("music"):
            result_audio = data["result"]["music"]
            url_audio = result_audio["url"]
            title_audio = result_audio["title"]
            media_audio = await Tools.get_media_data(url_audio, "mp3")
            audio_group.append(InputMediaAudio(media=media_audio))
            audio += 1
        if not media_group and not audio_group:
            return await proses.edit(f"{em.gagal}**No HD media found to send**")

        media_chunks = chunk_media_group(media_group)
        await proses.delete()

        for i, chunk in enumerate(media_chunks, 1):
            try:
                await client.send_media_group(chat_id=message.chat.id, media=chunk)
            except Exception as chunk_error:
                err += f"\n❌ Error sending chunk {i}: {str(chunk_error)}"
        if audio_group:
            for i, song in enumerate(audio_group, 1):
                try:
                    await client.send_audio(
                        chat_id=message.chat.id,
                        audio=song.media,
                        title=title_audio,
                    )
                except Exception as e:
                    err += f"Error sending audio {i}: {str(e)}\n"
        return await message.reply(
            f"{em.sukses}**Successfully sent {len(media_group)} media\n📸 Photos: `{foto}` | 🎥 Videos: `{video}` | 🎙 Audio: `{audio}`**\n{err}"
        )

    except Exception as er:
        logger.error(f"ttdl: {traceback.format_exc()}")
        return await proses.edit(f"{em.gagal}**An error occurred:** `{str(er)}`")


async def twitter_cmd(client, message, proses, arg):
    em = Emoji(client)
    await em.get()
    await proses.edit(f"{em.proses}**Wait a minute this takes some time...**")
    foto, video = 0, 0
    err = ""

    try:
        url = f"https://api.maelyn.sbs/api/x?url={arg}&apikey={API_MAELYN}"
        response = await Tools.fetch.get(url)

        if response.status_code != 200:
            return await proses.edit(
                f"{em.gagal}**Request failed with status code {response.status_code}**"
            )

        data = response.json()
        result = data.get("result", {})
        medias = result.get("medias", [])

        if not medias:
            return await proses.edit(f"{em.gagal}**No media found in the tweet.**")

        await proses.edit(f"{em.proses}**Preparing media for sending...**")
        media_group = []

        for item in medias:
            if item.get("extension") == "jpg":
                media = await Tools.get_media_data(item["url"], "jpg")
                media_group.append(InputMediaPhoto(media=media))
                foto += 1

        first_mp4 = next((i for i in medias if i.get("extension") == "mp4"), None)
        if first_mp4:
            media = await Tools.get_media_data(first_mp4["url"], "mp4")
            media_group.append(InputMediaVideo(media=media))
            video += 1

        if not media_group:
            return await proses.edit(
                f"{em.gagal}**Failed to prepare any media for sending.**"
            )

        media_chunks = chunk_media_group(media_group)
        await proses.delete()

        for i, chunk in enumerate(media_chunks, 1):
            try:
                await client.send_media_group(chat_id=message.chat.id, media=chunk)
            except Exception as chunk_error:
                err += f"Error sending chunk {i}: {str(chunk_error)}\n"

        return await message.reply(
            f"{em.sukses}**Successfully sent {len(media_group)} media.**\n📸 Photos: `{foto}` | 🎥 Videos: `{video}`\n{err}"
        )

    except Exception as er:
        logger.error(f"twdl: {traceback.format_exc()}")
        return await proses.edit(f"{em.gagal}**ERROR:** {str(er)}")


async def pindl_cmd(client, message, proses, arg):
    em = Emoji(client)
    await em.get()
    await proses.edit(f"{em.proses}**Wait a minute this takes some time...**")
    data_json = {"url": arg}
    url = "https://api.siputzx.my.id/api/d/pinterest"
    response = await Tools.fetch.post(url, json=data_json)

    if response.status_code != 200:
        return await proses.edit(
            f"{em.gagal}**Failed to download from the provided URL.**"
        )
    data = response.json()
    result = data["data"]["media_urls"][0]
    quality = result["quality"]
    if quality == "original":
        if result["type"] == "image":
            await message.reply_photo(
                result["url"], caption=data["data"]["title"] or ""
            )
        elif result["type"] == "video/mp4":
            await message.reply_video(
                result["video"], caption=data["data"]["title"] or ""
            )
    else:
        await message.reply(f"{em.gagal}**No original link found.**")

    return await proses.delete()


async def thread_cmd(client, message, proses, arg):
    em = Emoji(client)
    await em.get()
    await proses.edit(f"{em.proses}**Wait a minute this takes some time...**")
    foto, video = 0, 0
    err = ""

    try:
        url = f"https://api.maelyn.sbs/api/threads?url={arg}&apikey={API_MAELYN}"
        response = await Tools.fetch.get(url)

        if response.status_code != 200:
            return await proses.edit(
                f"{em.gagal}**Request failed with status code {response.status_code}**"
            )

        data = response.json()
        result = data.get("result", {})

        if not result:
            return await proses.edit(f"{em.gagal}**No media found in the tweet.**")

        await proses.edit(f"{em.proses}**Preparing media for sending...**")
        photo_url = result.get("image_urls")
        video_url = result.get("video_urls")
        media_group = []
        if len(photo_url) != 0:
            for item in photo_url:
                media = await Tools.get_media_data(item, "jpg")
                media_group.append(InputMediaPhoto(media=media))
                foto += 1

        if len(video_url) != 0:
            for item in video_url:
                media = await Tools.get_media_data(item["download_url"], "mp4")
                media_group.append(InputMediaVideo(media=media))
                video += 1

        if not media_group:
            return await proses.edit(
                f"{em.gagal}**Failed to prepare any media for sending.**"
            )

        media_chunks = chunk_media_group(media_group)
        await proses.delete()

        for i, chunk in enumerate(media_chunks, 1):
            try:
                await client.send_media_group(chat_id=message.chat.id, media=chunk)
            except Exception as chunk_error:
                err += f"Error sending chunk {i}: {str(chunk_error)}\n"

        return await message.reply(
            f"{em.sukses}**Successfully sent {len(media_group)} media.**\n📸 Photos: `{foto}` | 🎥 Videos: `{video}`\n{err}"
        )

    except Exception as er:
        logger.error(f"twdl: {traceback.format_exc()}")
        return await proses.edit(f"{em.gagal}**ERROR:** {str(er)}")


async def downloader_cmd(client, message):
    em = Emoji(client)
    await em.get()
    proses = await animate_proses(message, em.proses)

    reply = message.reply_to_message
    if reply:
        if message.chat.type in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
            get_msg = await client.get_messages(message.chat.id, reply.id)
            return await Tools.download_media(get_msg, client, proses, message)
    else:
        arg = client.get_text(message)
        prefix = client.get_prefix(client.me.id)
        if not arg:
            return await message.reply(
                f"{em.gagal}<b>Please give a link!\nExample: `{message.text.split()[0]} https://x.com/eskacangkhu/status/1921732123213398212?t=72ASOxnYYvYCltwOHzuXrw&s=19`</b>"
            )
        if not arg.startswith("https"):
            return await message.reply(
                f"{em.gagal}<b>Only link supported, if you want search with query use command: `{prefix[0]}sosmed bh terbang`.</b>"
            )
        await proses.edit(f"{em.proses}**Wait a minute this takes some time...**")

        try:
            # INSTAGRAM
            if "instagram.com" in arg:
                await proses.edit(f"{em.proses}**Detected Instagram link...**")
                return await instadl_cmd(client, message, proses, arg)

            # PINTEREST
            elif "pin.it" in arg:
                await proses.edit(f"{em.proses}**Detected Pinterest link...**")
                return await pindl_cmd(client, message, proses, arg)

            # TWITTER
            elif "x.com" in arg or "twitter.com" in arg:
                await proses.edit(f"{em.proses}**Detected Twitter link...**")
                return await twitter_cmd(client, message, proses, arg)

            # TELEGRAM
            elif "t.me" in arg:
                await proses.edit(f"{em.proses}**Detected Telegram link...**")
                return await teledl_cmd(client, message, proses, arg)

            # TIKTOK
            elif "tiktok.com" in arg or "vt.tiktok.com" in arg:
                await proses.edit(f"{em.proses}**Detected TikTok link...**")
                return await ttdl_cmd(client, message, proses, arg)

            # SPOTIFY
            elif "spotify.com" in arg:
                await proses.edit(f"{em.proses}**Detected Spotify link...**")
                return await spotdl_cmd(client, message, proses, arg)

            # YOUTUBE
            elif "youtube.com" in arg or "youtu.be" in arg:
                await proses.edit(f"{em.proses}**Detected YouTube link...**")
                return await ytvideo_cmd(client, message, proses, arg)

            elif "threads.com" in arg or "threads" in arg:
                await proses.edit(f"{em.proses}**Detected YouTube link...**")
                return await thread_cmd(client, message, proses, arg)

            else:
                return await proses.edit(
                    f"{em.gagal}**Unsupported link detected! Only support:**\n• Instagram\n• TikTok\n• Spotify\n• YouTube"
                )

        except Exception as er:
            logger.error(f"sosmeddl: {traceback.format_exc()}")
            return await proses.edit(f"{em.gagal}**An error occurred:** `{str(er)}`")


async def tiktok_search(client, message):
    em = Emoji(client)
    await em.get()
    query = client.get_text(message)
    if not query:
        return await message.reply(
            f"{em.gagal}<b>Please give query\nExample: `{message.text.split()[0]} bh terbang` or `{message.text.split()[0]} garam & madu`</b>"
        )
    proses = await animate_proses(message, em.proses)
    try:
        url = "https://api.siputzx.my.id/api/s/tiktok"
        data_json = {"query": query}
        err = ""
        media_group = []
        video = 0
        response = await Tools.fetch.post(url, json=data_json)
        if response.status_code != 200:
            return await proses.edit(f"{em.gagal}**Please try again later!**")
        data = response.json()["data"]
        for v in data:
            media_data = await Tools.get_media_data(v["play"], "mp4")
            media_group.append(InputMediaVideo(media=media_data))
            video += 1
        media_chunks = chunk_media_group(media_group)
        if not media_group:
            return await proses.edit(f"{em.gagal}**No media found.**")
        await proses.delete()
        for i, chunk in enumerate(media_chunks, 1):
            try:
                await client.send_media_group(chat_id=message.chat.id, media=chunk)
            except Exception as chunk_error:
                err += f"\n❌ Error sending chunk {i}: {str(chunk_error)}"
        return await message.reply(
            f"{em.sukses}**Successfully sent {len(media_group)} media\n🎥 Videos: `{video}`**\n{err}"
        )
    except Exception as er:
        logger.error(f"ttdl: {traceback.format_exc()}")
        return await message.reply(f"{em.gagal}**An error occurred:** `{str(er)}`")


async def pinterst_search(client, message):
    em = Emoji(client)
    await em.get()
    query = client.get_text(message)
    if not query:
        return await message.reply(
            f"{em.gagal}<b>Please give query\nExample: `{message.text.split()[0]} bh terbang` or `{message.text.split()[0]} garam & madu`</b>"
        )
    proses = await animate_proses(message, em.proses)
    try:
        url = "https://api.siputzx.my.id/api/s/pinterest"
        data_json = {"query": query, "type": ""}
        err = ""
        media_group = []
        foto, video = 0, 0
        response = await Tools.fetch.post(url, json=data_json)
        if response.status_code != 200:
            return await proses.edit(f"{em.gagal}**Please try again later!**")
        data = response.json()["data"]
        for v in data:
            if v["video_url"]:
                media_data = await Tools.get_media_data(v["video_url"], "mp4")
                media_group.append(InputMediaVideo(media=media_data))
                video += 1
            elif v["image_url"]:
                media_data = await Tools.get_media_data(v["image_url"], "jpg")
                media_group.append(InputMediaPhoto(media=media_data))
                foto += 1
        media_chunks = chunk_media_group(media_group)
        if not media_group:
            return await proses.edit(f"{em.gagal}**No media found.**")
        await proses.delete()
        for i, chunk in enumerate(media_chunks, 1):
            try:
                await client.send_media_group(chat_id=message.chat.id, media=chunk)
            except Exception as chunk_error:
                err += f"\n❌ Error sending chunk {i}: {str(chunk_error)}"
        return await message.reply(
            f"{em.sukses}**Successfully sent {len(media_group)} media\n📸 Photos: `{foto}` | 🎥 Videos: `{video}`**\n{err}"
        )
    except Exception as er:
        logger.error(f"ttdl: {traceback.format_exc()}")
        return await message.reply(f"{em.gagal}**An error occurred:** `{str(er)}`")


async def spotify_search(client, message):
    em = Emoji(client)
    await em.get()
    query = client.get_text(message)
    if not query:
        return await message.reply(
            f"{em.gagal}<b>Please give query\nExample: `{message.text.split()[0]} bh terbang` or `{message.text.split()[0]} garam & madu`</b>"
        )
    proses = await animate_proses(message, em.proses)
    data_json = {"query": query}
    url = "https://api.siputzx.my.id/api/s/spotify"
    response = await Tools.fetch.post(url, json=data_json)
    if response.status_code != 200:
        return await proses.edit(f"{em.gagal}**Please try again later!**")
    uniq = f"{str(uuid4())}"
    data = response.json()["data"]
    state.set(uniq.split("-")[0], uniq.split("-")[0], data)
    state.set(uniq.split("-")[0], "idm_spotdl", id(message))
    inline = await ButtonUtils.send_inline_bot_result(
        message,
        message.chat.id,
        bot.me.username,
        f"inline_spotify {uniq.split('-')[0]}",
    )
    if inline:
        await proses.delete()
    else:
        return await proses.edit(f"{em.gagal}**ERROR Please contact developer.*")


async def youtube_search(client, message):
    em = Emoji(client)
    await em.get()
    query = client.get_text(message)
    if not query:
        return await message.reply(
            f"{em.gagal}<b>Please give query\nExample: `{message.text.split()[0]} bh terbang` or `{message.text.split()[0]} garam & madu`</b>"
        )
    proses = await animate_proses(message, em.proses)
    data_json = {"query": query}
    url = "https://api.siputzx.my.id/api/s/youtube"
    response = await Tools.fetch.post(url, json=data_json)
    if response.status_code != 200:
        return await proses.edit(f"{em.gagal}**Please try again later!**")
    uniq = f"{str(uuid4())}"
    data = response.json()["data"]
    state.set(uniq.split("-")[0], uniq.split("-")[0], data)
    state.set(uniq.split("-")[0], "idm_ytsearch", id(message))
    as_video = True if message.command[0] == "vsong" else False
    state.set(uniq.split("-")[0], "as_video", as_video)
    inline = await ButtonUtils.send_inline_bot_result(
        message,
        message.chat.id,
        bot.me.username,
        f"inline_youtube {uniq.split('-')[0]}",
    )
    if inline:
        await proses.delete()
    else:
        return await proses.edit(f"{em.gagal}**ERROR Please contact developer.*")
