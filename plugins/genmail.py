__MODULES__ = "Mail"
__HELP__ = """<blockquote>Command Help **Temp Mail**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can generate fake email from this command**
        `{0}mail gen`
    **After you generate fake mail, get otp from this command**
        `{0}mail otp` (id)
    **You can view list email after you generated**
        `{0}mail list`</blockquote>
<b>   {1}</b>
"""
IS_PRO = True

from command import mail_cmd
from helpers import CMD


@CMD.UBOT("mail")
async def _(client, message):
    return await mail_cmd(client, message)
