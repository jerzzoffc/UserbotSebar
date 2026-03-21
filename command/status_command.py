from time import time

from pyrogram.raw.functions import Ping
from pyrogram.types import ReplyKeyboardRemove
from pytz import timezone

from clients import navy
from config import BOT_NAME, SUDO_OWNERS
from database import dB
from helpers import get_time, start_time


async def cek_status_akun(client, message):
    user_id = message.from_user.id
    seles = await dB.get_list_from_var(client.me.id, "SELLER")
    if user_id not in navy._get_my_id:
        status2 = "tidak aktif"
    else:
        status2 = "aktif"
    if user_id in SUDO_OWNERS:
        status = "<b>[Admins]</b>"
    elif user_id in seles:
        status = "<b>[Seller]</b>"
    else:
        status = "<b>[Costumer]</b>"
    uptime = await get_time((time() - start_time))
    await client.invoke(Ping(ping_id=0))
    exp = await dB.get_expired_date(user_id)
    habis = (
        exp.astimezone(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M")
        if exp
        else "None"
    )
    prefix = client.get_prefix(user_id)
    plan = await dB.get_var(user_id, "plan")
    is_pro = "Pro" if plan == "is_pro" else "Basic"
    _token = await dB.get_token(user_id)
    user_token = _token["token"] if _token else "-"
    return await message.reply(
        f"""
<blockquote expandable>
<b>{BOT_NAME}</b>
    <b>Status Ubot:</b> <code>{status2}</code>
      <b>Status Pengguna:</b> <i>{status}</i>
      <b>Plan:</b> <b>{is_pro}</b>
      <b>Prefixes :</b> <code>{' '.join(prefix)}</code>
      <b>Tanggal Kedaluwarsa:</b> <code>{habis}</code>
      <b>Uptime Ubot:</b> <code>{uptime}</code>
      <b>Token:</b><code>{user_token}</code>
</blockquote>
""",
        reply_markup=ReplyKeyboardRemove(),
    )
