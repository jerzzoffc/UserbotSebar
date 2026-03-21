import asyncio
import os
from datetime import datetime, timedelta
from uuid import uuid4

from clients import bot
from database import dB
from helpers import Emoji, Message, Saweria, Tools, animate_proses

transactions = {}


async def saweria_cmd(client, message):
    em = Emoji(client)
    await em.get()

    proses = await animate_proses(message, em.proses)
    args = ["login", "qris"]
    command = message.command

    if len(command) < 2 or command[1] not in args:
        return await proses.edit(
            f"{em.gagal}**Please give me valid query: `login`, `qris`**"
        )
    if command[1] == "login":
        if not message.reply_to_message:
            return await proses.edit(
                f"{em.gagal}**Usage:** `{message.text.split()[0]} login (reply to message with format: email@.com username)`"
            )
        email, username = Tools.parse_text(message.reply_to_message)
        saweria_userid = await Saweria.get_user_id(username)
        if saweria_userid is None:
            return await proses.edit(f"{em.gagal}**Please try again.**")
        data = {
            "saweria_userid": saweria_userid,
            "saweria_email": email,
            "saweria_username": username,
        }
        await dB.set_var(client.me.id, "SAWERIA_ACCOUNT", data)
        return await proses.edit(
            f"{em.sukses}**Successfully logged in to Saweria! Your userId: `{saweria_userid}`**"
        )
    elif command[1] == "qris":
        info = await dB.get_var(client.me.id, "SAWERIA_ACCOUNT")
        if not info:
            return await proses.edit(
                f"{em.gagal}**Please login first using `login` command.**"
            )
        if len(command) < 4:
            return await proses.edit(
                f"{em.gagal}**Usage:** `{message.text.split()[0]} qris 5000 beli kopi`"
            )
        try:
            amount = int(command[2])
        except ValueError:
            return await proses.edit(f"{em.gagal}**Amount must be a number!**")

        desc = " ".join(command[3:])
        uniq = f"{str(uuid4())}"
        output_path = f"/storage/cache/{uniq}.png"
        saweria_email = info["saweria_email"]
        saweria_username = info["saweria_username"]
        saweria_userid = info["saweria_userid"]
        qrstring, hasil_idpayment, qris_path = await Saweria.create_payment_qr(
            saweria_userid, saweria_username, amount, saweria_email, output_path
        )
        hasil_amount = Saweria.get_amount(qrstring)
        hasil_expired = datetime.now() + timedelta(minutes=3)

        sent = await message.reply_photo(
            qris_path,
            caption=(
                f"""
<b>📃「 Waiting Payment 」</b>

<blockquote expandable><b><i>{em.profil}Item: `{desc}`
{em.net}Price: `{Message.format_rupiah(amount)}`
{em.speed}Total Payment: `{Message.format_rupiah(hasil_amount)}`
{em.warn}Expires At: `{hasil_expired}`

Scan QRIS above to pay.</i></b></blockquote>

<blockquote>© Auto Payment @{bot.me.username}</blockquote>
"""
            ),
        )
        if os.path.exists(qris_path):
            os.remove(qris_path)
        await proses.delete()
        transactions[uniq.split("-")[0]] = {
            "expire_time": hasil_expired,
            "message_id": sent.id,
            "done": False,
        }
        while True:
            await asyncio.sleep(1)
            trans = transactions.get(uniq.split("-")[0])
            if not trans or trans["done"]:
                break
            if datetime.now() > trans["expire_time"]:
                if not trans["done"]:
                    await client.send_message(
                        message.chat.id,
                        f"{em.gagal}<b><i>Payment canceled due to timeout.</i></b>",
                    )
                    await client.delete_messages(
                        chat_id=message.chat.id,
                        message_ids=trans["message_id"],
                    )
                    del transactions[uniq.split("-")[0]]
                break
            try:
                is_paid = await Saweria.check_paid_status(hasil_idpayment)
                if is_paid and not trans["done"]:
                    trans["done"] = True
                    await message.reply(
                        f"""
<blockquote><b><i>{em.sukses}Payment received!

{em.profil}Item: `{desc}`
{em.net}Price: `{Message.format_rupiah(amount)}`
{em.speed}Total Paid: `{Message.format_rupiah(hasil_amount)}`</i></b></blockquote>
"""
                    )
                    await client.delete_messages(
                        chat_id=message.chat.id,
                        message_ids=transactions[uniq.split("-")[0]]["message_id"],
                    )
                    del transactions[uniq.split("-")[0]]
                    return

            except Exception as e:
                print(f"Error checking payment: {e}")
                if uniq.split("-")[0] in transactions:
                    del transactions[uniq.split("-")[0]]
                await message.reply(f"{em.gagal}**Error occurred:** `{str(e)}`")
                break
