__MODULES__ = "Download"
__HELP__ = """<blockquote>Command Help **Download**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can download any media from link**
        `{0}dl` (url)

    **Supported links**:
        - instagram
        - pinterest
        - twitter
        - telegram
        - tiktok
        - spotify
        - threads
        - youtube</blockquote>
<b>   {1}</b>
"""


from command import downloader_cmd
from helpers import CMD


@CMD.UBOT("dl")
async def _(client, message):
    return await downloader_cmd(client, message)
