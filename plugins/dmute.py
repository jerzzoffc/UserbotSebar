from clients import navy
from command import deleter_cmd, force_del_cmd
from helpers import CMD

IS_PRO = True

__MODULES__ = "Dmute"
__HELP__ = """<blockquote>Command Help **Dmute**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Added user to database dmute**
        `{0}dmute` (username)
    **Remove user from database dmute**
        `{0}undmute` (number)
    **View user on dmute database**
        `{0}getdmute`</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("dmute|undmute|getdmute")
async def _(client, message):
    return await deleter_cmd(client, message)


@CMD.NO_CMD("FORCE_DEL", navy)
async def _(client, message):
    return await force_del_cmd(client, message)
