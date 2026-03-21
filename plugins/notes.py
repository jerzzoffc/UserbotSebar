from command import clearnotes_cmd, getnote_cmd, listnotes_cmd, savenote_cmd
from helpers import CMD

__MODULES__ = "Notes"
__HELP__ = """<blockquote>Command Help **Notes**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can save message with this command**
        `{0}save` (note name) (reply message)
    **Get saved message you are**
        `{0}get` (note name)
    **View all saved note**
        `{0}notes`
    **You can clear or delete the one note or many note**
        `{0}clear` (note name) or (name1, name2, name2)
    **For this command you can delete all saved note**
        `{0}clear all`</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("save")
async def _(client, message):
    return await savenote_cmd(client, message)


@CMD.UBOT("get")
async def _(client, message):
    return await getnote_cmd(client, message)


@CMD.UBOT("notes")
async def _(client, message):
    return await listnotes_cmd(client, message)


@CMD.UBOT("clear")
async def _(client, message):
    return await clearnotes_cmd(client, message)
