from command import (joinos_cmd, joinvc_cmd, leavevc_cmd, listner_cmd,
                     startvc_cmd, stopvc_cmd, turunos_cmd, vctitle_cmd)
from helpers import CMD

__MODULES__ = "Vctools"
__HELP__ = """<blockquote>Command Help **VcTools**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Start voice chat group/channel**
        `{0}startvc` 
    **End voice chat group/channel**
        `{0}stopvc`
    **Join voice chat group/channel**
        `{0}joinvc` (chatid)
    **Leave voice chat group/channel**
        `{0}leavevc` (chatid)</blockquote>

<blockquote expandable>--**Others Commands**--

    **Check listeners from voice chat**
        `{0}listeners`
    **Edit title voice chat group**
        `{0}vctitle` (title)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("startvc")
@CMD.ONLY_GROUP
async def _(client, message):
    return await startvc_cmd(client, message)


@CMD.UBOT("stopvc")
@CMD.ONLY_GROUP
async def _(client, message):
    return await stopvc_cmd(client, message)


@CMD.UBOT("joinvc|jvc")
async def _(client, message):
    return await joinvc_cmd(client, message)


@CMD.UBOT("leavevc|lvc")
async def _(client, message):
    return await leavevc_cmd(client, message)


@CMD.UBOT("listeners")
@CMD.ONLY_GROUP
async def _(client, message):
    return await listner_cmd(client, message)


@CMD.UBOT("vctitle")
@CMD.ONLY_GROUP
async def _(client, message):
    return await vctitle_cmd(client, message)


@CMD.UBOT("joinos")
@CMD.FAKE_NLX
async def _(client, message):
    return await joinos_cmd(client, message)


@CMD.UBOT("turunos")
@CMD.FAKE_NLX
async def _(client, message):
    return await turunos_cmd(client, message)
