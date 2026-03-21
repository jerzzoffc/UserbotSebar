__MODULES__ = "News"
__HELP__ = """<blockquote>Command Help **News**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can get news from CNN Indonesia**
        `{0}news`</blockquote>
<b>   {1}</b>
"""
IS_PRO = True


from command import detcnn_cmd
from helpers import CMD


@CMD.UBOT("news")
async def _(client, message):
    return await detcnn_cmd(client, message)
