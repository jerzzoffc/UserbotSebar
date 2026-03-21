from uuid import uuid4

from clients import bot
from database import state
from helpers import ButtonUtils, Emoji, Tools, animate_proses


async def gempa_cmd(client, message):
    em = Emoji(client)
    await em.get()

    proses = await animate_proses(message, em.proses)
    try:
        url = "https://api.siputzx.my.id/api/info/bmkg"
        result = await Tools.fetch.post(url)
        if result.status_code != 200:
            return await proses.edit(f"{em.gagal}**Please try again later!!**")
        data = result.json()["data"]
        uniq = f"{str(uuid4())}"
        state.set(uniq.split("-")[0], uniq.split("-")[0], data)
        inline = await ButtonUtils.send_inline_bot_result(
            message,
            message.chat.id,
            bot.me.username,
            f"inline_bmkg {uniq.split('-')[0]}",
        )
        if inline:
            return await message.delete()
    except Exception as er:
        await message.reply(f"{em.gagal}**ERROR**: {str(er)}")
    return await proses.delete()
