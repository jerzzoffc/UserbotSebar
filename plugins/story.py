__MODULES__ = "Story"
__HELP__ = """<blockquote>Command Help **Story**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can post media to telegram story** 
        `{0}story post` (reply media)
    **Get all stories on your account**
        `{0}story cek`
    **You can delete story with this command**
        `{0}story del` (strory id)
    **You can steal story from user**
        `{0}story get` (url)</blockquote>
<b>   {1}</b>
"""
IS_PRO = True

from command import story_cmd
from helpers import CMD


@CMD.UBOT("story")
async def _(client, message):
    return await story_cmd(client, message)
