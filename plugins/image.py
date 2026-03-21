from command import (blur_cmd, gif_cmd, miror_cmd, negative_cmd, pic_cmd,
                     rbg_cmd, waifu_cmd)
from helpers import CMD

__MODULES__ = "Image"
__HELP__ = """<blockquote>Command Help **Image**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can remove background from image**
        `{0}rbg` (reply image)
    **Add effect blur to image**
        `{0}blur` (reply image)
    **You can flip mirror the image**
        `{0}mirror` (reply image)
    **Add negative effect to image**
        `{0}negative` (reply image)</blockquote>

<blockquote expandable>--**Search Commands**--

    **Get awesome image for wallpaper**
        `{0}wall`
    **Get beautiful anime image**
        `{0}waifu`
    **Get image with your command**
        `{0}pic` (prompt)
    **Get gif with your command**
        `{0}gif` (prompt)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("rbg")
async def _(client, message):
    return await rbg_cmd(client, message)


@CMD.UBOT("blur")
async def _(client, message):
    return await blur_cmd(client, message)


@CMD.UBOT("negative")
async def _(client, message):
    return await negative_cmd(client, message)


@CMD.UBOT("miror")
async def _(client, message):
    return await miror_cmd(client, message)


@CMD.UBOT("wall|waifu")
async def _(client, message):
    return await waifu_cmd(client, message)


@CMD.UBOT("pic")
async def _(client, message):
    return await pic_cmd(client, message)


@CMD.UBOT("gif")
async def _(client, message):
    return await gif_cmd(client, message)
