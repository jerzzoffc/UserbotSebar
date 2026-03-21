from clients import navy
from command import auto_reply_trigger, chatbot_cmd
from helpers import CMD

__MODULES__ = "Chatbot"
__HELP__ = """<blockquote>Command Help **chatbot**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can turned on chatbot in group chat**
        `{0}chatbot` (on)
    **You can turned off chatbot in group chat**
        `{0}chatbot` (off)
    **You can turned on chatbot from admins in group chat**
        `{0}chatbot admin` (on)
    **You can turned off chatbot from admins in group chat**
        `{0}chatbot admin` (off)
    **You can turned on chatbot for allchats if someone reply your messages**
        `{0}chatbot reply` (on)
    **You can turned off chatbot for allchats if someone reply your messages**
        `{0}chatbot reply` (off)
    **You can ignore chatbot for user in group chat**
        `{0}chatbot ignore` (userID/reply user)
    **You can reignore chatbot for user  in group chat**
        `{0}chatbot reignore` (userID/reply user)
    **You can check status on database**
        `{0}chatbot` (status)
    **You can set role for chatbot**
        `{0}chatbot` (role)

**Note:** This feature will work if someone replies to your message.</blockquote>
<b>   {1}</b>
"""

IS_PRO = True


@CMD.UBOT("chatbot")
async def _(client, message):
    return await chatbot_cmd(client, message)


@CMD.NO_CMD("CHATBOT", navy)
async def _(client, message):
    return await auto_reply_trigger(client, message)
