import traceback

import config
from helpers import Emoji, Tools, animate_proses


async def cuaca_cmd(client, message):
    em = Emoji(client)
    await em.get()
    prs = await animate_proses(message, em.proses)

    prompt = client.get_text(message)
    if not prompt:
        return await prs.edit(
            f"{em.gagal}**Please provide a location!\n"
            f"Example: `{message.text.split()[0]} jakarta`**"
        )

    headers = {"mg-apikey": config.API_MAELYN}
    params = {"q": prompt}
    url = "https://api.maelyn.sbs/api/cuaca"

    respon = await Tools.fetch.get(url, headers=headers, params=params)

    if respon.status_code != 200:
        return await prs.edit(
            f"{em.gagal}**Failed to fetch weather data! Status code: {respon.status_code}**"
        )

    try:
        data = respon.json().get("result", {})
        kota = data.get("city", "-")
        suhu = data.get("temperature", "-")
        angin = data.get("wind", "-")
        kelembaban = data.get("humidity", "-")
        cuaca = data.get("weather", "-")
        deskripsi = data.get("description", "-")
        tekanan = data.get("pressure", "-")
        latitude = data.get("latitude", "-")
        longitude = data.get("longitude", "-")

        short_address = f"{cuaca} — {deskripsi}, Suhu: {suhu}"

        detail_text = (
            f"🌤️ **Cuaca Saat Ini**\n\n"
            f"📍 Lokasi: `{kota}`\n"
            f"📍 Koordinat: `{latitude}, {longitude}`\n"
            f"🌡️ Suhu: `{suhu}`\n"
            f"💧 Kelembaban: `{kelembaban}`\n"
            f"☁️ Cuaca: `{cuaca}` — `{deskripsi}`\n"
            f"🌬️ Angin: `{angin}`\n"
            f"📈 Tekanan Udara: `{tekanan}`"
        )

        venue_msg = await message.reply_venue(
            latitude=latitude,
            longitude=longitude,
            title=str(kota),
            address=short_address[:128],
            quote=True,
        )

        await message.reply(detail_text, reply_to_message_id=venue_msg.id)

    except Exception as e:
        print(traceback.format_exc())
        await message.reply(f"{em.gagal}**ERROR:** `{str(e)}`")

    return await prs.delete()
