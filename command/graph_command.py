from pyrogram import enums
from telegraph.aio import Telegraph

from clients import bot
from helpers import Emoji, Tools, animate_proses


def format_size(size_in_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.1024


async def post_to_telegraph(is_media: bool, title=None, content=None, media=None):
    telegraph = Telegraph()
    if telegraph.get_access_token() is None:
        await telegraph.create_account(short_name=bot.me.username)
    if is_media:
        response = await telegraph.upload_file(media)
        return f"https://img.yasirweb.eu.org{response[0]['src']}"
    response = await telegraph.create_page(
        title,
        html_content=content,
        author_url=f"https://t.me/{bot.me.username}",
        author_name=bot.me.username,
    )
    return f"https://graph.org/{response['path']}"


async def tg_cmd(client, message):
    emo = Emoji(client)
    await emo.get()
    XD = await animate_proses(message, emo.proses)
    if not message.reply_to_message:
        return await XD.edit(f"{emo.gagal}**Please reply to message text or video!**")
    if message.reply_to_message.text:
        page_title = f"{client.me.first_name} {client.me.last_name or ''}"
        page_text = message.reply_to_message.text
        page_text = page_text.replace("\n", "<br>")
        try:
            url = await post_to_telegraph(False, page_title, page_text)
        except Exception as exc:
            return await XD.edit(f"{emo.gagal}**{exc}**")
        await XD.delete()
        return await message.reply(
            f"{emo.sukses}**Successfully Uploaded: <a href='{url}'>Click Here</a>**",
            disable_web_page_preview=True,
        )
    else:
        data = Tools.get_file_id(message.reply_to_message)
        file_size = data.get("file_size")
        media_name = data.get("file_name") or data.get("file_unique_id")
        if file_size > 100 * 1024 * 1024:
            return await XD.edit(f"{emo.gagal}**File size: `{file_size}` is to large**")
        await XD.edit(f"{emo.proses}**Please wait uploading `{media_name}`...**")
        try:
            url = await Tools.upload_media(message)
        except Exception as exc:
            return await XD.edit(f"{emo.gagal}**{exc}**")
        # html_link = HTML.html_link(url, media_name)
        await XD.delete()
        return await message.reply(
            f"{emo.sukses}<b>Successfully Uploaded: {url}</b>",
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML,
        )
