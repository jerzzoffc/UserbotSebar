__MODULES__ = "Gemini"
__HELP__ = """<blockquote>Command Help **Gemini**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can answer question to Gemini ai** 
        `{0}gemini` (question) 
    **You can answer about image to Gemini ai** 
        `{0}gemini` (reply photo) (question) 
    **You can asnwer about video to Gemini ai** 
        `{0}gemini` (reply video) (question)</blockquote>
<b>   {1}</b>
"""

IS_PRO = True


from command import gemini_cmd
from helpers import CMD


@CMD.UBOT("gemini")
async def _(client, message):
    return await gemini_cmd(client, message)
