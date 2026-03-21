import asyncio
import random
from random import choice

from pyrogram import enums, types

from helpers import Emoji, animate_proses


async def asupan_cmd(client, message):
    em = Emoji(client)
    await em.get()

    y = await animate_proses(message, em.proses)
    await asyncio.sleep(3)
    try:
        asupannya = []
        async for asupan in client.search_messages(
            "@AsupanNyaSaiki", filter=enums.MessagesFilter.VIDEO
        ):
            asupannya.append(asupan)
        video = random.choice(asupannya)
        try:
            await video.copy(
                message.chat.id,
                caption=f"{em.sukses}<b>Upload by: <a href=tg://user?id={client.me.id}>{client.me.first_name} {client.me.last_name or ''}</a></b>",
                reply_to_message_id=message.id,
            )
        except Exception:
            await message.reply(f"{em.gagal}**Sorry cannot send media here.**")
        return await y.delete()
    except Exception:
        return await y.edit(f"{em.gagal}<b>Try a gain!</b>")


async def cewe_cmd(client, message):
    em = Emoji(client)
    await em.get()

    y = await animate_proses(message, em.proses)
    await asyncio.sleep(3)
    try:
        ayangnya = []
        async for ayang in client.search_messages(
            "@AyangSaiki", filter=enums.MessagesFilter.PHOTO
        ):
            ayangnya.append(ayang)
        photo = random.choice(ayangnya)
        try:
            await photo.copy(
                message.chat.id,
                caption=f"{em.sukses}<b>Upload by: <a href=tg://user?id={client.me.id}>{client.me.first_name} {client.me.last_name or ''}</a></b>",
                reply_to_message_id=message.id,
            )
        except Exception:
            await message.reply(f"{em.gagal}**Sorry cannot send media here.**")
        return await y.delete()
    except Exception:
        return await y.edit(f"{em.gagal}<b>Try a gain!</b>")


async def cowo_cmd(client, message):
    em = Emoji(client)
    await em.get()

    y = await animate_proses(message, em.proses)
    await asyncio.sleep(3)
    try:
        ayang2nya = []
        async for ayang2 in client.search_messages(
            "@Ayang2Saiki", filter=enums.MessagesFilter.PHOTO
        ):
            ayang2nya.append(ayang2)
        photo = random.choice(ayang2nya)
        try:
            await photo.copy(
                message.chat.id,
                caption=f"{em.sukses}<b>Upload by: <a href=tg://user?id={client.me.id}>{client.me.first_name} {client.me.last_name or ''}</a></b>",
                reply_to_message_id=message.id,
            )
        except Exception:
            await message.reply(f"{em.gagal}**Sorry cannot send media here.**")
        return await y.delete()
    except Exception:
        return await y.edit(f"{em.gagal}<b>Try a gain!</b>")


async def pap_cmd(client, message):
    em = Emoji(client)
    await em.get()

    y = await animate_proses(message, em.proses)
    await asyncio.sleep(3)
    try:
        await message.reply_photo(
            choice(
                [
                    lol.photo.file_id
                    async for lol in client.search_messages(
                        "@mm_kyran", filter=enums.MessagesFilter.PHOTO
                    )
                ]
            ),
            False,
            caption=f"{em.sukses}<b>Ange ga kamu???</b>",
        )
    except Exception:
        await message.reply(f"{em.gagal}**Sorry cannot send media here.**")
    return await y.delete()


async def ppcp_cmd(client, message):
    emo = Emoji(client)
    await emo.get()
    pros = await animate_proses(message, emo.proses)

    url = "medialuci"
    ppcp_pairs = []

    try:
        photos = []
        async for media in client.search_messages(
            url, filter=enums.MessagesFilter.PHOTO
        ):
            photos.append(media.photo.file_id)

        if len(photos) < 2:
            return await pros.edit(
                f"{emo.gagal}<b>Gagal menemukan pasangan foto profil. Coba lagi nanti.</b>"
            )

        for i in range(0, len(photos) - 1, 2):
            ppcp_pairs.append([photos[i], photos[i + 1]])

        selected_pair = random.choice(ppcp_pairs)

        media_group = [types.InputMediaPhoto(photo) for photo in selected_pair]
        try:
            await client.send_media_group(
                message.chat.id,
                media=media_group,
                reply_to_message_id=message.id,
            )
        except Exception:
            await message.reply(f"{emo.gagal}**Sorry cannot send media here.**")
        return await pros.delete()

    except Exception as error:
        await pros.edit(f"{emo.gagal}<b>Error:</b>\n<code>{error}</code>")
