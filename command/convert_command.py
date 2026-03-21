import asyncio
import base64
import io
import json
import os
import random
import subprocess
import traceback
import uuid
from io import BytesIO

import cv2
import gtts
import requests
import speech_recognition as sr
from bs4 import BeautifulSoup
from gpytranslate import Translator
from PIL import Image
from pyrogram import raw, types
from pyrogram.enums import MessageMediaType
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from config import API_MAELYN, SUDO_OWNERS
from database import dB
from helpers import (ApiImage, Emoji, Message, Quotly, Sticker, Tools,
                     animate_proses)


def download_website(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount("http://", HTTPAdapter(max_retries=retries))

    try:
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return (
                f"Failed to download source code. Status code: {response.status_code}"
            )

    except Exception as e:
        return f"An error occurred: {str(e)}"


async def ReTrieveFile(input_file_name):
    headers = {
        "X-API-Key": "3RCCWg8tMBfDWdAs44YMfJmC",
    }
    files = {
        "image_file": (input_file_name, open(input_file_name, "rb")),
    }
    return requests.post(
        "https://api.remove.bg/v1.0/removebg",
        headers=headers,
        files=files,
        allow_redirects=True,
        stream=True,
    )


async def rbg_cmd(client, message):
    em = Emoji(client)
    await em.get()

    proses = await animate_proses(message, em.proses)
    if message.reply_to_message:
        reply_message = message.reply_to_message

        try:
            if (
                isinstance(reply_message.media, raw.types.MessageMediaPhoto)
                or reply_message.media
            ):
                downloaded_file_name = await client.download_media(
                    reply_message, "./downloads/"
                )
                await proses.edit(f"<b>{em.gagal}Try removing background...</b>")
                output_file_name = await ReTrieveFile(downloaded_file_name)
                os.remove(downloaded_file_name)
            else:
                return await proses.edit(f"<b>{em.gagal}Please reply to photo!!</b>")
        except Exception as e:
            await proses.edit(f"{em.gagal}**ERROR:** {(str(e))}")
            return
        contentType = output_file_name.headers.get("content-type")
        if "image" in contentType:
            with io.BytesIO(output_file_name.content) as remove_bg_image:
                remove_bg_image.name = "rbg.png"
                await client.send_document(
                    message.chat.id,
                    document=remove_bg_image,
                    force_document=True,
                    reply_to_message_id=message.id,
                )
                return await proses.delete()
        else:
            return await proses.edit(
                "{}<b>ERROR</b>\n<i>{}</i>".format(
                    em.gagal, output_file_name.content.decode("UTF-8")
                )
            )
    else:
        return await message.reply(f"<b>{em.gagal}Please reply to photo</b>")


async def blur_cmd(client, message):
    em = Emoji(client)
    await em.get()

    reply = message.reply_to_message
    proses = await animate_proses(message, em.proses)
    if not reply:
        return await proses.edit(f"<b>{em.gagal}Please reply to photo</b>")
    yinsxd = await client.download_media(reply, "./downloads/")
    if yinsxd.endswith(".tgs"):
        cmd = ["lottie_convert.py", yinsxd, "yin.png"]
        file = "yin.png"
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    else:
        img = cv2.VideoCapture(yinsxd)
        heh, lol = img.read()
        cv2.imwrite("yin.png", lol)
        file = "yin.png"
    yin = cv2.imread(file)
    ayiinxd = cv2.GaussianBlur(yin, (35, 35), 0)
    cv2.imwrite("yin.jpg", ayiinxd)
    await client.send_photo(
        message.chat.id,
        "yin.jpg",
        reply_to_message_id=message.id,
    )
    os.remove("yin.png")
    os.remove("yin.jpg")
    os.remove(yinsxd)
    return await proses.delete()


async def negative_cmd(client, message):
    em = Emoji(client)
    await em.get()

    reply = message.reply_to_message
    proses = await animate_proses(message, em.proses)
    if not reply:
        return await proses.edit(f"<b>{em.gagal}Please reply to photo</b>")
    ayiinxd = await client.download_media(reply, "./downloads/")
    if ayiinxd.endswith(".tgs"):
        cmd = ["lottie_convert.py", ayiinxd, "yin.png"]
        file = "yin.png"
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    else:
        img = cv2.VideoCapture(ayiinxd)
        heh, lol = img.read()
        cv2.imwrite("yin.png", lol)
        file = "yin.png"
    yinsex = cv2.imread(file)
    kntlxd = cv2.bitwise_not(yinsex)
    cv2.imwrite("yin.jpg", kntlxd)
    await client.send_photo(
        message.chat.id,
        "yin.jpg",
        reply_to_message_id=message.id,
    )
    os.remove("yin.png")
    os.remove("yin.jpg")
    os.remove(ayiinxd)
    return await proses.delete()


async def miror_cmd(client, message):
    em = Emoji(client)
    await em.get()

    reply = message.reply_to_message
    proses = await animate_proses(message, em.proses)
    if not reply:
        return await proses.edit(f"<b>{em.gagal}Please reply to photo.</b>")
    xnproses = await client.download_media(reply, "./downloads/")
    if xnproses.endswith(".tgs"):
        cmd = ["lottie_convert.py", xnproses, "yin.png"]
        file = "yin.png"
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    else:
        img = cv2.VideoCapture(xnproses)
        kont, tol = img.read()
        cv2.imwrite("yin.png", tol)
        file = "yin.png"
    yin = cv2.imread(file)
    mmk = cv2.flip(yin, 1)
    ayiinxd = cv2.hconcat([yin, mmk])
    cv2.imwrite("yin.jpg", ayiinxd)
    await client.send_photo(
        message.chat.id,
        "yin.jpg",
        reply_to_message_id=message.id,
    )
    os.remove("yin.png")
    os.remove("yin.jpg")
    os.remove(xnproses)
    return await proses.delete()


async def waifu_cmd(client, message):
    em = Emoji(client)
    await em.get()

    message.reply_to_message
    proses = await animate_proses(message, em.proses)
    if message.command[0] == "wall":
        photo = await ApiImage.wall(client)
        try:
            await photo.copy(message.chat.id, reply_to_message_id=message.id)
            return await proses.delete()
        except Exception as error:
            return await proses.edit(f"{em.gagal}**{str(error)}**")
    elif message.command[0] == "waifu":
        photo = ApiImage.waifu()
        try:
            await message.reply_photo(photo)
            return await proses.delete()
        except Exception as error:
            return await proses.edit(f"{em.gagal}**{str(error)}**")


async def pic_cmd(client, message):
    em = Emoji(client)
    await em.get()

    prompt = client.get_text(message)
    proses = await animate_proses(message, em.proses)
    await asyncio.sleep(2)
    if not prompt:
        return await proses.edit(
            f"{em.gagal}**Please use command:** <code>{message.text.split()[0]} dino kuning</code>"
        )
    x = await client.get_inline_bot_results(message.command[0], prompt)
    await proses.delete()
    get_media = []
    for X in range(5):
        try:
            saved = await client.send_inline_bot_result(
                client.me.id, x.query_id, x.results[random.randrange(30)].id
            )
            saved = await client.get_messages(
                client.me.id, int(saved.updates[1].message.id), replies=0
            )
            get_media.append(types.InputMediaPhoto(saved.photo.file_id))
        except Exception as er:
            return await proses.edit(f"{em.gagal}<b>Image nothing found</b> {str(er)}")
    await saved.delete()
    return await client.send_media_group(
        message.chat.id,
        get_media,
        reply_to_message_id=message.id,
    )


async def gif_cmd(client, message):
    em = Emoji(client)
    await em.get()

    prompt = client.get_text(message)
    proses = await animate_proses(message, em.proses)
    await asyncio.sleep(2)
    if not prompt:
        return await proses.edit(
            f"{em.gagal}**Please use command: <code>{message.text.split()[0]} dino kuning</code>"
        )
    x = await client.get_inline_bot_results(message.command[0], prompt)
    await proses.delete()
    try:
        saved = await client.send_inline_bot_result(
            client.me.id, x.query_id, x.results[random.randrange(30)].id
        )
    except Exception as er:
        await proses.edit(f"{em.gagal}<b>Media nothing found</b> {str(er)}")
    saved = await client.get_messages(
        client.me.id, int(saved.updates[1].message.id), replies=0
    )
    await saved.delete()
    return await client.send_animation(
        message.chat.id, saved.animation.file_id, reply_to_message_id=message.id
    )


async def toimg_cmd(client, message):
    em = Emoji(client)
    await em.get()

    proses = await animate_proses(message, em.proses)
    reply = message.reply_to_message
    try:
        file_io = await Tools.dl_pic(client, reply)
        file_io.name = "sticker.png"
        await message.reply_photo(file_io)
        return await proses.delete()
    except Exception as e:
        return await proses.edit(f"{em.gagal}**ERROR:** {str(e)}")


async def tosticker_cmd(client, message):
    em = Emoji(client)
    await em.get()

    proses = await animate_proses(message, em.proses)
    try:
        if not message.reply_to_message or not message.reply_to_message.photo:
            return await proses.edit(f"<b>{em.gagal}**Please reply to photo!!**</b>")
        sticker = await client.download_media(
            message.reply_to_message.photo.file_id,
            f"sticker_{message.from_user.id}.webp",
        )
        await message.reply_sticker(sticker)
        os.remove(sticker)
        return await proses.delete()
    except Exception as e:
        return await proses.edit(f"{em.gagal}**ERROR:** {str(e)}")


async def togif_cmd(client, message):
    em = Emoji(client)
    await em.get()

    proses = await animate_proses(message, em.proses)
    if not message.reply_to_message.sticker:
        return await proses.edit(f"<b>{em.gagal}Please reply to sticker!!</b>")
    file = await client.download_media(
        message.reply_to_message,
        f"gift_{message.from_user.id}.mp4",
    )
    try:
        await client.send_animation(
            message.chat.id, file, reply_to_message_id=message.id
        )
        os.remove(file)
        return await proses.delete()
    except Exception as error:
        return await proses.edit(f"{em.gagal}**ERROR:** {str(error)}")


async def toaudio_cmd(client, message):
    em = Emoji(client)
    await em.get()

    proses = await animate_proses(message, em.proses)
    replied = message.reply_to_message
    if not replied:
        return await proses.edit(f"<b>{em.gagal}Please reply to message video!</b>")
    if replied.media == MessageMediaType.VIDEO:
        await proses.edit(f"<b>{em.proses}Downloading video...</b>")
        file = await client.download_media(
            message=replied,
            file_name=f"toaudio_{replied.id}",
        )
        out_file = f"{file}.mp3"
        try:
            await proses.edit(f"<b>{em.proses}Converting audio...</b>")
            cmd = f"ffmpeg -i {file} -q:a 0 -map a {out_file}"
            await client.run_cmd(cmd)
            await proses.edit(f"<b>{em.proses}Try to sending audio...</b>")
            await client.send_voice(
                message.chat.id,
                voice=out_file,
                reply_to_message_id=message.id,
            )
            os.remove(file)
            return await proses.delete()
        except Exception as error:
            await proses.edit(f"{em.gagal}**ERROR:** {str(error)}")
    else:
        return await proses.edit(f"<b>{em.gagal}Please reply to video!!</b>")


async def img2text_cmd(client, message):
    em = Emoji(client)
    await em.get()

    prs = await animate_proses(message, em.proses)
    reply = message.reply_to_message
    if not reply:
        return await prs.edit(f"{em.gagal}**Please reply to image!!**")
    if reply and not reply.photo:
        return await prs.edit(f"{em.gagal}**Please reply to image!!**")
    arg = await Tools.maelyn_upload(message)
    url = f"https://api.maelyn.sbs/api/img2txt/prompt?url={arg}&apikey={API_MAELYN}"
    respon = await Tools.fetch.get(url)
    await prs.edit(f"{em.proses}**Scanning of image...**")
    if respon.status_code != 200:
        return await prs.edit(
            f"{em.gagal}**Please try again later: {respon.status_code}**"
        )
    data = respon.json().get("result")
    if not data:
        return await prs.edit(
            f"{em.gagal}**Please try again later: {respon.status_code}**"
        )
    try:
        await message.reply(
            f"{em.sukses}**Media:** <a href='{reply.link}'>Here</a>\n**Result:** `{data}`",
            disable_web_page_preview=True,
        )
        return await prs.delete()
    except Exception as er:
        await prs.delete()
        return await message.reply(f"{em.gagal}**ERROR:** {str(er)}")


async def mmf_cmd(client, message):
    emo = Emoji(client)
    await emo.get()
    pref = client.get_prefix(client.me.id)
    x = next(iter(pref))
    rep = message.reply_to_message
    meme = None
    file = None

    if not rep:
        return await message.reply(
            f"{emo.gagal}<b>Use the command by replying to a photo/sticker/video.</b>"
        )

    if not (rep.photo or rep.animation or rep.video or rep.sticker):
        return await message.reply(
            f"{emo.gagal}<b>Reply to a photo, sticker, or video.</b>"
        )

    try:
        file = await client.download_media(rep)
        if not file:
            return await message.reply(f"{emo.gagal}<b>Failed to download media.</b>")

        pros = await message.reply(
            f"{emo.proses}<b>Processing adding text to media ..</b>"
        )

        text = client.get_text(message)
        if len(message.command) < 2:
            await pros.edit(
                f"{emo.gagal}<b>Use the command by adding text after the command.\n\nExample:\n<code>{x}mmf Hi;Love!</code>\n\nThen the text <i><u>Hi</u></i> will be at the top of the media, and the text <i><u>Love!</u></i> will be at the bottom of the media.</b>"
            )
            return

        if rep.animation or rep.video:
            meme = await Sticker.add_text_to_video(file, text)
        else:
            meme = await Sticker.add_text_img(file, text)

        await client.send_sticker(
            message.chat.id, sticker=meme, reply_to_message_id=message.id
        )
        await pros.delete()

    except Exception as e:
        await message.reply(f"{emo.gagal}<b>Error processing media: {str(e)}</b>")
        if "pros" in locals():
            await pros.delete()

    finally:
        if file and os.path.exists(file):
            try:
                os.remove(file)
            except Exception:
                pass

        if meme and os.path.exists(meme):
            try:
                os.remove(meme)
            except Exception:
                pass


def run_curl(cmd):
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.stdout.decode().strip(), process.stderr.decode().strip()


async def qrcode_cmd(client, message):
    em = Emoji(client)
    await em.get()

    proses = await animate_proses(message, em.proses)
    if len(message.command) < 2:
        return await proses.edit(
            f"{em.gagal}**Please give valid query `{message.text.split()[0]}` [gen or read]!**"
        )
    query = message.command[1]
    reply = message.reply_to_message or message

    if query == "gen":
        if not reply or reply and not reply.text:
            return await proses.edit(f"{em.gagal}**Please give barcode text**")
        text = reply.text or reply.caption
        data = (
            Tools.qr_gen(text)
            if reply
            else Tools.qr_gen(message.text.split(None, 2)[2])
        )
        try:
            QRcode = (
                requests.post(
                    "https://api.qrcode-monkey.com//qr/custom",
                    json=data,
                )
                .json()["imageUrl"]
                .replace("//api", "https://api")
            )
            await client.send_photo(
                message.chat.id, QRcode, reply_to_message_id=reply.id
            )
            return await proses.delete()
        except Exception as error:
            return await proses.edit(f"{em.gagal}**ERROR**: {str(error)}")

    elif query == "read":
        if not (reply and reply.media and (reply.photo or reply.sticker)):
            await proses.edit(f"{em.gagal}**Please reply to valid barcode!**")
            return
        if not os.path.isdir("downloads/"):
            os.makedirs("downloads/")
        down_load = await client.download_media(message=reply, file_name="downloads/")
        cmd = [
            "curl",
            "-X",
            "POST",
            "-F",
            "f=@" + down_load + "",
            "https://zxing.org/w/decode",
        ]
        stdout, stderr = await asyncio.to_thread(run_curl, cmd)
        os.remove(down_load)
        if not (stdout or stderr):
            await proses.edit(f"{em.gagal}**Something error, try again!**")
            return
        try:
            soup = BeautifulSoup(stdout, "html.parser")
            qr_contents = soup.find_all("pre")[0].text
        except IndexError:
            await proses.edit(f"{em.gagal}**Something error, try again!**")
            return
        return await proses.edit(
            f"{em.sukses}<b>Qr Text:</b>\n<code>{qr_contents}</code>"
        )
    else:
        return await proses.edit(
            f"{em.gagal}**Please give valid query `{message.text.split()[0]}` [gen or read]!**"
        )


async def consu(dok):
    try:
        with open(dok, "rb") as file:
            data_bytes = file.read()
        json_data = json.loads(data_bytes)
        image_data_base64 = json_data.get("image")
        if not image_data_base64:
            raise ValueError("Tidak ada data gambar dalam JSON")
        image_data = base64.b64decode(image_data_base64)
        image_io = io.BytesIO(image_data)
        image_io.name = "Quotly.webp"
        return image_io
    except Exception as e:
        raise e


async def qcolor_cmd(client, message):
    em = Emoji(client)
    await em.get()
    iymek = f"\n•".join(Quotly.colors)
    jadi = f"{em.sukses}Color for quotly\n•"
    if len(iymek) > 4096:
        with open("qcolor.txt", "w") as file:
            file.write(iymek)
        await message.reply_document(
            "qcolor.txt", caption=f"{em.sukses}Color for quotly"
        )
        os.remove("qcolor.txt")
        return
    else:
        return await message.reply(jadi + iymek)


async def qoutly_cmd(client, message):
    em = Emoji(client)
    await em.get()

    if not message.reply_to_message:
        return await message.reply(f"{em.gagal}**Please reply to a message!**")

    pros = await animate_proses(message, em.proses)
    reply_msg = message.reply_to_message
    cmd = message.command[1:]
    print(f"Cmd: {cmd}")

    def get_color(index=0):
        return cmd[index] if len(cmd) > index else random.choice(Quotly.colors)

    try:
        if not cmd:
            payload = {
                "type": "quote",
                "format": "png",
                "backgroundColor": get_color(),
                "messages": [],
            }
            sid, title, name = await Quotly.forward_info(reply_msg)
            messages_json = {
                "entities": Tools.get_msg_entities(reply_msg),
                "avatar": True,
                "from": {
                    "id": sid,
                    "title": title,
                    "name": name,
                    "emoji_status": await Quotly.get_emoji(reply_msg),
                },
                "text": await Quotly.t_or_c(reply_msg),
                "replyMessage": {},
            }
            payload["messages"].append(messages_json)
        elif cmd[0].startswith("@"):
            color = get_color(1)
            include_reply = len(cmd) > 2 and cmd[2] == "-r"
            payload = {
                "type": "quote",
                "format": "png",
                "backgroundColor": color,
                "messages": [],
            }
            username = cmd[0][1:]
            user = await client.get_users(username)
            if user.id in SUDO_OWNERS:
                return await pros.edit(f"{em.gagal}**You can't quote this user**")

            fake_msg = user
            name = fake_msg.first_name
            if fake_msg.last_name:
                name += f" {fake_msg.last_name}"

            emoji_status = None
            if fake_msg.emoji_status:
                emoji_status = str(fake_msg.emoji_status.custom_emoji_id)

            if include_reply:
                replied = reply_msg.reply_to_message
                reply_message = Quotly.parse_reply_info(replied)
            else:
                reply_message = {}

            messages_json = {
                "entities": Tools.get_msg_entities(reply_msg),
                "avatar": True,
                "from": {
                    "id": fake_msg.id,
                    "title": name,
                    "name": name,
                    "emoji_status": emoji_status,
                },
                "text": await Quotly.t_or_c(reply_msg),
                "replyMessage": reply_message,
            }

            payload["messages"].append(messages_json)
        elif cmd[0].startswith("-r"):
            replied = reply_msg.reply_to_message
            reply_message = Quotly.parse_reply_info(replied)
            payload = {
                "type": "quote",
                "format": "png",
                "backgroundColor": get_color(1),
                "messages": [],
            }
            sid, title, name = await Quotly.forward_info(reply_msg)
            messages_json = {
                "entities": Tools.get_msg_entities(reply_msg),
                "avatar": True,
                "from": {
                    "id": sid,
                    "title": title,
                    "name": name,
                    "emoji_status": await Quotly.get_emoji(reply_msg),
                },
                "text": await Quotly.t_or_c(reply_msg),
                "replyMessage": reply_message,
            }
            payload["messages"].append(messages_json)
        elif cmd[0].isdigit():
            payload = {
                "type": "quote",
                "format": "png",
                "backgroundColor": get_color(1),
                "messages": [],
                "scale": 2,
            }
            sid, title, name = await Quotly.forward_info(reply_msg)
            messages_json = {
                "entities": Tools.get_msg_entities(reply_msg),
                "avatar": True,
                "from": {
                    "id": sid,
                    "title": title,
                    "name": name,
                    "emoji_status": await Quotly.get_emoji(reply_msg),
                },
                "text": await Quotly.t_or_c(reply_msg),
                "replyMessage": {},
            }
            payload["messages"].append(messages_json)
            count = int(cmd[0])
            if count > 10:
                return await pros.edit(f"{em.gagal}**Max 10 messages**")
            async for msg in client.get_chat_history(
                reply_msg.chat.id, limit=count, offset_id=reply_msg.id
            ):
                sid, title, name = await Quotly.forward_info(msg)
                messages_json = {
                    "entities": Tools.get_msg_entities(msg),
                    "avatar": True,
                    "from": {
                        "id": sid,
                        "title": title,
                        "name": name,
                        "emoji_status": await Quotly.get_emoji(msg),
                    },
                    "text": await Quotly.t_or_c(msg),
                    "replyMessage": {},
                }
                payload["messages"].append(messages_json)
            payload["messages"].reverse()
        else:
            payload = {
                "type": "quote",
                "format": "png",
                "backgroundColor": cmd[0],
                "messages": [],
            }
            sid, title, name = await Quotly.forward_info(reply_msg)
            messages_json = {
                "entities": Tools.get_msg_entities(reply_msg),
                "avatar": True,
                "from": {
                    "id": sid,
                    "title": title,
                    "name": name,
                    "emoji_status": await Quotly.get_emoji(reply_msg),
                },
                "text": await Quotly.t_or_c(reply_msg),
            }
            payload["messages"].append(messages_json)
        hasil = await Quotly.quotly(payload)
        bio_sticker = BytesIO(hasil)
        bio_sticker.name = "biosticker.webp"
        await message.reply_sticker(bio_sticker)
        await pros.delete()

    except Exception as e:
        print(f"ERROR: {traceback.format_exc()}")
        return await pros.edit(f"{em.gagal}{e}")


async def textgen_cmd(client, message):
    em = Emoji(client)
    await em.get()

    prs = await animate_proses(message, em.proses)
    prompt = client.get_text(message)

    if not prompt:
        return await prs.edit(
            f"{em.gagal}<b>Give the query you want to generate prompt!\n\nExample: \n<code>{message.text.split()[0]} cat on the beach</code></b>"
        )
    url = f"https://api.maelyn.sbs/api/generator/prompt?q={prompt}&apikey={API_MAELYN}"
    respon = await Tools.fetch.get(url)
    if respon.status_code == 200:
        data = respon.json()["result"]
        try:
            await prs.edit(f"`{data}`")
        except Exception as er:
            await prs.delete()
            return await message.reply(f"{em.gagal}**ERROR:** {str(er)}")
    else:
        return await prs.edit(f"**{em.gagal}Please try again: {respon.status_code}!**")


async def tiny_cmd(client, message):
    em = Emoji(client)
    await em.get()
    await Sticker.dl_font()
    rep = message.reply_to_message

    pros = await animate_proses(message, em.proses)
    if not rep:
        return await pros.edit(f"{em.gagal}**Please reply to sticker or photo!**")
    doc = await client.download_media(rep)
    im1 = Image.open("font-module/bahan2.png")
    if doc.endswith(".tgs"):
        await client.download_media(rep, "man.tgs")
        await Tools.bash("lottie_convert.py man.tgs json.json")
        json = open("json.json", "r")
        jsn = json.read()
        jsn = jsn.replace("512", "2000")
        ("json.json", "w").write(jsn)
        await Tools.bash("lottie_convert.py json.json man.tgs")
        file = "man.tgs"
        os.remove("json.json")
    elif doc.endswith((".gif", ".mp4")):
        idoc = cv2.VideoCapture(doc)
        busy = idoc.read()
        cv2.imwrite("i.png", busy)
        fil = "i.png"
        im = Image.open(fil)
        z, d = im.size
        if z == d:
            xxx, yyy = 200, 200
        else:
            t = z + d
            a = z / t
            b = d / t
            aa = (a * 100) - 50
            bb = (b * 100) - 50
            xxx = 200 + 5 * aa
            yyy = 200 + 5 * bb
        k = im.resize((int(xxx), int(yyy)))
        k.save("k.png", format="PNG", optimize=True)
        im2 = Image.open("k.png")
        back_im = im1.copy()
        back_im.paste(im2, (150, 0))
        back_im.save("o.webp", "WEBP", quality=95)
        file = "o.webp"
        os.remove(fil)
        os.remove("k.png")
    else:
        im = Image.open(doc)
        z, d = im.size
        if z == d:
            xxx, yyy = 200, 200
        else:
            t = z + d
            a = z / t
            b = d / t
            aa = (a * 100) - 50
            bb = (b * 100) - 50
            xxx = 200 + 5 * aa
            yyy = 200 + 5 * bb
        k = im.resize((int(xxx), int(yyy)))
        k.save("k.png", format="PNG", optimize=True)
        im2 = Image.open("k.png")
        back_im = im1.copy()
        back_im.paste(im2, (150, 0))
        back_im.save("o.webp", "WEBP", quality=95)
        file = "o.webp"
        os.remove("k.png")
    await asyncio.gather(
        pros.delete(),
        client.send_sticker(
            message.chat.id,
            sticker=file,
            reply_to_message_id=Message.ReplyCheck(message),
        ),
    )
    os.remove(file)
    os.remove(doc)
    return


async def tr_cmd(client, message):
    em = Emoji(client)
    await em.get()
    trans = Translator()

    pros = await animate_proses(message, em.proses)
    bhs = await client.get_translate()
    if message.reply_to_message:

        txt = message.reply_to_message.text or message.reply_to_message.caption
        src = await trans.detect(txt)
    else:
        if len(message.command) < 2:
            return await message.reply(
                f"{em.gagal}**Please reply to message text or give text!**"
            )
        else:
            txt = message.text.split(None, 1)[1]
            src = await trans.detect(txt)
    trsl = await trans(txt, sourcelang=src, targetlang=bhs)
    reply = f"{em.sukses} Translated:\n\n{trsl.text}"
    rep = message.reply_to_message or message
    await pros.delete()
    return await client.send_message(message.chat.id, reply, reply_to_message_id=rep.id)


async def lang_cmd(client, message):
    em = Emoji(client)
    await em.get()
    try:
        bhs_list = "\n".join(
            f"- **{lang}**: `{code}`" for lang, code in Tools.kode_bahasa.items()
        )
        return await message.reply(f"{em.sukses}**Language codes:**\n\n{bhs_list}")

    except Exception as e:
        return await message.reply(f"{em.gagal}**Error: {str(e)}**")


async def setlang_cmd(client, message):
    em = Emoji(client)
    await em.get()

    pros = await message.reply(f"{em.proses}**Processing...**")
    if len(message.command) < 2:
        return await pros.edit(
            f"{em.gagal}**Please reply to message text or give text!**"
        )

    for lang, code in Tools.kode_bahasa.items():
        kd = message.text.split(None, 1)[1]
        if kd.lower() == code.lower():
            await dB.set_var(client.me.id, "_translate", kd.lower())
            return await pros.edit(
                f"{em.sukses}**Successfully changed translate language to: {lang}-{kd}**"
            )


async def vremover_cmd(client, message):
    em = Emoji(client)
    await em.get()

    prs = await animate_proses(message, em.proses)
    rep = message.reply_to_message or message
    if not rep or not (rep.audio, rep.video):
        return await prs.edit(f"{em.gagal}**Please reply to audio or video!!**")
    arg = await Tools.upload_media(message)
    url = f"https://api.betabotz.eu.org/api/tools/voiceremover?url={arg}&apikey="
    respon = await Tools.fetch.get(url)
    ex = await message.reply(f"{em.proses}**Try to extract of instruments...**")

    if respon.status_code == 200:
        data = respon.json()["result"]
        try:
            await prs.delete()
            voice = data["vocal_path"]
            audio = data["instrumental_path"]
            send_voice = await client.send_audio(
                message.chat.id, voice, caption=f"<b>Vocal</b>"
            )
            send_audio = await client.send_audio(
                message.chat.id, audio, caption=f"<b>Instruments</b>"
            )
            await ex.delete()
            return await message.reply(
                f"{em.sukses}<blockquote expandable>**Status error:** {data['error']}\n**Status message:** {data['message']}\n**Vocal of the <a href='{rep.link}'>media</a>:** <a href='{send_voice.link}'>here</a>\n**Instruments of the <a href='{rep.link}'>media</a>:** <a href='{send_audio.link}'>here</a></blockquote>",
                disable_web_page_preview=True,
            )
        except Exception as er:
            await ex.delete()

            return await message.reply(f"{em.gagal}**ERROR:** {str(er)}")
    else:
        return await message.reply(
            f"**{em.gagal}Please try again: {respon.status_code}!**"
        )


async def tts_cmd(client, message):
    em = Emoji(client)
    await em.get()

    pros = await animate_proses(message, em.proses)
    bhs = await client.get_translate()
    reply = message.reply_to_message or message
    if len(message.command) == 1 and not reply:
        return await pros.edit(
            f"{em.gagal}**Please reply to message text or give text!**"
        )
    if reply:
        if not reply.text or reply.caption:
            return await pros.edit(
                f"{em.gagal}**Please reply to message text or give text!**"
            )
    kata = client.get_text(message)
    gts = gtts.gTTS(kata, lang=bhs)
    gts.save("trs.oog")
    try:
        await client.send_voice(
            chat_id=message.chat.id,
            voice="trs.oog",
            reply_to_message_id=reply.id,
        )
        await pros.delete()
        os.remove("trs.oog")
        return
    except Exception as er:
        return await pros.edit(f"{em.gagal}**Error: {str(er)}**")

    except FileNotFoundError:
        return


async def stt_cmd(client, message):
    em = Emoji(client)
    await em.get()

    proses = await animate_proses(message, em.proses)
    reply = message.reply_to_message
    if not reply or not reply.media:
        return await proses.edit(f"{em.gagal}**Please reply to message media**")
    bhs = await client.get_translate()
    try:
        file_path = await reply.download()
        wav_path = file_path + ".wav"
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                file_path,
                "-acodec",
                "pcm_s16le",
                "-ar",
                "16000",
                wav_path,
            ],
            check=True,
        )

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language=bhs)
                await proses.edit(
                    f"{em.sukses}**Converted [message]({reply.link}):**\n{text}",
                    disable_web_page_preview=True,
                )
            except sr.UnknownValueError:
                return await proses.edit(
                    f"{em.gagal}**Sorry, I can't recognize the sound.**"
                )
            except sr.RequestError:
                return await proses.edit(
                    f"{em.gagal}**Sorry, there is a problem with the voice recognition service.**"
                )

            finally:
                if os.path.exists(wav_path):
                    os.remove(wav_path)
                if os.path.exists(file_path):
                    os.remove(file_path)

    except subprocess.CalledProcessError:
        return await proses.edit(f"{em.gagal}**Failed to convert audio files.**")


async def webdl_cmd(client, message):
    if len(message.command) == 1:
        await message.reply_text(
            "**Please enter a URL along with the /webdl command.**"
        )
        return

    url = message.command[1]

    source_code = download_website(url)
    if source_code.startswith("An error occurred") or source_code.startswith(
        "Failed to download"
    ):
        return await message.reply_text(source_code)
    else:
        with open("website.txt", "w", encoding="utf-8") as file:
            file.write(source_code)
        return await message.reply_document(
            document="website.txt", caption=f"**Source code of {url}**"
        )


async def webss_cmd(client, message):
    em = Emoji(client)
    await em.get()

    proses = await animate_proses(message, em.proses)
    if len(message.command) < 2:
        return await proses.edit(
            f"{em.gagal}**Please give valid link! Example: `{message.text.split()[0]}webss https://youtube.com`**"
        )
    link = (
        message.text.split(None, 1)[1]
        if len(message.command) < 3
        else message.text.split(None, 2)[1]
    )
    if "https://" not in link:
        return await proses.edit(f"{em.gagal}**Please give valid link!**")
    full = "mobile" if len(message.command) < 3 else "desktop"
    try:
        url = "https://api.siputzx.my.id/api/tools/ssweb"
        payload = {"url": link, "theme": "dark", "device": full}
        response = await Tools.fetch.post(url, json=payload)
        if response.status_code != 200:
            return await proses.edit(f"{em.gagal}**Please another url.**")
        content_type = response.headers.get("Content-Type", "")
        if content_type != "image/png":
            return await proses.edit(f"{em.gagal}**Please another url.**")
        file_path = f"webss_{uuid.uuid4().hex}.png"
        with open(file_path, "wb") as f:
            f.write(response.content)
        await proses.delete()
        return await message.reply_photo(file_path)
    except Exception as r:
        return await message.reply(f"{em.gagal}**ERROR:** {str(r)}")
