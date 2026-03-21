from command import addpack_cmd, gstick_cmd, kang_cmd, unkang_cmd
from helpers import CMD

__MODULES__ = "Sticker"
__HELP__ = """<blockquote>Command Help **Sticker**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Add sticker to your pack**
        `{0}kang` (reply sticker)
    **Add pack to new your pack**
        `{0}addpack` (reply sticker)
    **Delete sticker from your pack**
        `{0}unkang` (reply sticker)
    **Get information from sticker with this command**
        `{0}gstik` (reply sticker)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("gstik|getstiker|getsticker")
async def _(client, message):
    return await gstick_cmd(client, message)


@CMD.UBOT("unkang")
async def _(client, message):
    return await unkang_cmd(client, message)


@CMD.UBOT("kang")
async def _(client, message):
    return await kang_cmd(client, message)


@CMD.UBOT("addpack")
async def _(client, message):
    return await addpack_cmd(client, message)
