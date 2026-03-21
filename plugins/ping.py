from command import absen_cmd, mping_cmd, settext_cmd
from helpers import CMD


@CMD.UBOT("set_text")
async def _(client, message):
    return await settext_cmd(client, message)


@CMD.DEV_CMD("mping")
@CMD.FAKEDEV("mping")
@CMD.UBOT("ping")
async def _(client, message):
    return await mping_cmd(client, message)


@CMD.FAKEDEV("absen")
@CMD.DEV_CMD("absen")
async def _(client, message):
    return await absen_cmd(client, message)
