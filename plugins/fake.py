from command import fstik_cmd, ftype_cmd, fvideo_cmd, fvoice_cmd, task_cmd
from helpers import CMD

IS_PRO = True

__MODULES__ = "Fake"
__HELP__ = """<blockquote>Command Help **Fake**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can fake send typing to chat, default duration is 3600 seconds**
        `{0}ftype` (seconds)
    **You can fake send video to chat, default duration is 3600 seconds**
        `{0}fvideo` (seconds)
    **You can fake send sticker to chat, default duration is 3600 seconds**
        `{0}fstik` (seconds)
    **You can fake send voice to chat, default duration is 3600 seconds**
        `{0}fvoice` (seconds)
        
    **This command for stop fake action**
        `{0}fcancel` (taskid)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("ftype")
async def _(client, message):
    return await ftype_cmd(client, message)


@CMD.UBOT("fvoice")
async def _(client, message):
    return await fvoice_cmd(client, message)


@CMD.UBOT("fvideo")
async def _(client, message):
    return await fvideo_cmd(client, message)


@CMD.UBOT("fstik")
async def _(client, message):
    return await fstik_cmd(client, message)


@CMD.UBOT("task")
async def _(client, message):
    return await task_cmd(client, message)
