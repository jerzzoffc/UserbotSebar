from command import toaudio_cmd, togif_cmd, toimg_cmd, tosticker_cmd
from helpers import CMD

__MODULES__ = "Convert"
__HELP__ = """<blockquote>Command Help **Convert**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Convert message stiker to photo if you want**
        `{0}toimg` (reply sticker)
    **You can change photo to sticker with this command**
        `{0}tosticker` (reply image)
    **You can convert video  to gif**
        `{0}togif` (reply video)
    **You can extract or convert the audio from replied video**
        `{0}toaudio` (reply video)</blockquote>
<b>   {1}</b>
"""
IS_BASIC = True


@CMD.UBOT("toimg")
async def _(client, message):
    return await toimg_cmd(client, message)


@CMD.UBOT("tosticker")
async def _(client, message):
    return await tosticker_cmd(client, message)


@CMD.UBOT("togif")
async def _(client, message):
    return await togif_cmd(client, message)


@CMD.UBOT("toaudio")
async def _(client, message):
    return await toaudio_cmd(client, message)
