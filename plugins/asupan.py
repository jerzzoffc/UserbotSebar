from command import asupan_cmd, cewe_cmd, cowo_cmd, pap_cmd, ppcp_cmd
from helpers import CMD

__MODULES__ = "Asupan"
__HELP__ = """<blockquote>Command Help **Asupan**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can get girl photo**
        `{0}cewek`
    **You can get boy photo**
        `{0}cowok`
    **You can get pap random**
        `{0}pap`
    **You can get couple photo**
        `{0}ppcp`
    **Get random asupan video**
        `{0}asupan`</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


@CMD.UBOT("asupan")
async def _(client, message):
    return await asupan_cmd(client, message)


@CMD.UBOT("cewek")
async def _(client, message):
    return await cewe_cmd(client, message)


@CMD.UBOT("cowok")
async def _(client, message):
    return await cowo_cmd(client, message)


@CMD.UBOT("pap")
async def _(client, message):
    return await pap_cmd(client, message)


@CMD.UBOT("ppcp")
async def _(client, message):
    return await ppcp_cmd(client, message)
