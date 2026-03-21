from command import setemoji_cmd
from helpers import CMD

__MODULES__ = "Emoji"
__HELP__ = """<blockquote>Command Help **Emoji**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can set ping emoji with this command**
        `{0}setemoji ping` (emoji)
    **You can set uptime emoji with this command**
        `{0}setemoji uptime` (emoji)
    **You can set profile emoji with this command**
        `{0}setemoji profil` (emoji)
    **You can set robot emoji with this command**
        `{0}setemoji robot` (emoji)

    **You can set msg emoji with this command**
        `{0}setemoji msg` (emoji)
    **You can set warn emoji with this command**
        `{0}setemoji warn` (emoji)
    **You can set block emoji with this command**
        `{0}setemoji block` (emoji)
    **You can set gagal emoji with this command**
        `{0}setemoji gagal` (emoji)
    
    **You can set sukses emoji with this command**
        `{0}setemoji sukses` (emoji)
    **You can set owner emoji with this command**
        `{0}setemoji owner` (emoji)
    **You can set klip emoji with this command**
        `{0}setemoji klip` (emoji)
    **You can set net emoji with this command**
        `{0}setemoji net` (emoji)

    **You can set up emoji with this command**
        `{0}setemoji up` (emoji)
    **You can set down emoji with this command**
        `{0}setemoji down` (emoji)
    **You can set speed emoji with this command**
        `{0}setemoji speed` (emoji)
    **You can set proses emoji with this command**
        `{0}setemoji proses` (emoji)
    **You can set status emoji with this command**
        `{0}setemoji status` (emoji)
        
    **You can set id emoji or media with this command**
        `{0}id` (reply message)
    **Get all youre emoji set**
        `{0}getemoji`
    **You can enable emoji**
        `{0}setemoji emoji on`
    **You can disable emoji**
        `{0}setemoji emoji off`
    
    
**Note**: Emoji status only working on premium users.</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


@CMD.UBOT("setemoji|getemoji")
async def _(client, message):
    return await setemoji_cmd(client, message)
