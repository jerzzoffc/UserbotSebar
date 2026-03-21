import traceback

from command import (an1cb, back_home, bola_date, bola_matches,
                     calculator_callback, callback_alert, cancel_payment,
                     cb_help, cb_markdown, cb_notes, cek_expired_cb,
                     cek_status_akun, chat_gpt, chose_plan, cine_plax,
                     closed_bot, closed_user, confirm_pay, contact_admins,
                     copy_msg, del_userbot, dl_spot, dl_ytsearch,
                     general_plugins, get_bio, get_font, gpt_voice,
                     kurang_tambah, mari_buat_userbot, moddycb, news_,
                     next_font, nxt_spotify, nxt_ytsearch, nxtbmkg, pm_warn,
                     prev_font, prevnext_userbot, prevnext_userbot2,
                     refresh_cat, reset_costum_text, reset_emoji, reset_prefix,
                     rest_anime, rest_comic, rest_donghua, restart_userbot,
                     selected_topic, token_cmd, tools_token, tools_userbot,
                     user_aggre, viewchord, viewgempa)
from helpers import CMD, trigger
from logs import logger


@CMD.REGEX(trigger)
async def _(client, message):
    try:
        text = message.text
        if text in [
            "✨ Mulai Buat Userbot",
            "✨ Pembuatan Ulang Userbot",
            "✅ Lanjutkan Buat Userbot",
        ]:
            return await mari_buat_userbot(client, message)
        elif text in ["💎 Plan Pro", "🧩 Plan Basic", "⚡ Plan Lite"]:
            return await general_plugins(client, message)
        elif text == "❓ Status Akun":
            return await cek_status_akun(client, message)
        elif text.startswith("🔄 Reset"):
            data = text.split(" ")[2]
            if data == "Emoji":
                return await reset_emoji(client, message)
            elif data == "Prefix":
                return await reset_prefix(client, message)
            elif data == "Text":
                return await reset_costum_text(client, message)
        elif text == "🔄 Restart Userbot":
            return await restart_userbot(client, message)
        elif text == "💬 Hubungi Admins":
            return await contact_admins(client, message)
        elif text == "🔑 Token":
            return await token_cmd(client, message)
    except Exception as er:
        logger.error(f"Terjadi error: {str(er)}")


@CMD.CALLBACK()
async def _(client, callback):
    try:
        query = callback.data
        logger.info(f"Name callback query: {query}")
        if query == "buttonclose":
            return await closed_bot(client, callback)
        elif query == "starthome":
            return await back_home(client, callback)

        elif query.startswith("close"):
            return await closed_user(client, callback)
        elif query.startswith("pm_warn"):
            return await pm_warn(client, callback)
        elif query.startswith("getbio_"):
            return await get_bio(client, callback)
        elif query.startswith("copymsg_"):
            return await copy_msg(client, callback)
        elif query.startswith("cb_"):
            return await cb_notes(client, callback)
        elif query.startswith("get_font"):
            return await get_font(client, callback)
        elif query.startswith("prev_font"):
            return await prev_font(client, callback)
        elif query.startswith("next_font"):
            return await next_font(client, callback)
        elif query.startswith("refresh_cat"):
            return await refresh_cat(client, callback)
        elif query.startswith("nxtspotify"):
            return await nxt_spotify(client, callback)
        elif query.startswith("dlspot"):
            return await dl_spot(client, callback)
        elif query.startswith("bola_date"):
            return await bola_date(client, callback)
        elif query.startswith("bola_matches"):
            return await bola_matches(client, callback)
        elif query.startswith("restanime_"):
            return await rest_anime(client, callback)
        elif query.startswith("restdonghua_"):
            return await rest_donghua(client, callback)
        elif query.startswith("restcomic_"):
            return await rest_comic(client, callback)
        elif query.startswith("news_"):
            return await news_(client, callback)
        elif query.startswith("chatgpt_"):
            return await chat_gpt(client, callback)
        elif query.startswith("gptvoice_"):
            return await gpt_voice(client, callback)
        elif query.startswith("cineplax"):
            return await cine_plax(client, callback)

        elif query == ("go_payment"):
            return await user_aggre(client, callback)
        elif query.startswith("kurang") or query.startswith("tambah"):
            return await kurang_tambah(client, callback)
        elif query.startswith("confirm"):
            return await confirm_pay(client, callback)
        elif query == ("batal_payment"):
            return await cancel_payment(client, callback)

        elif query.startswith("del_ubot"):
            return await del_userbot(client, callback)
        elif query.startswith("prev_ub") or query.startswith("next_ub"):
            return await prevnext_userbot(client, callback)
        elif query.startswith("fakeprev_ub") or query.startswith("fakenext_ub"):
            return await prevnext_userbot2(client, callback)
        elif (
            query.startswith("get_otp")
            or query.startswith("get_phone")
            or query.startswith("get_faktor")
            or query.startswith("ub_deak")
            or query.startswith("deak_akun")
        ):
            return await tools_userbot(client, callback)
        elif query.startswith("use_token") or query.startswith("revoke_token"):
            return await tools_token(client, callback)

        elif query.startswith("markdown"):
            return await cb_markdown(client, callback)
        elif query.startswith("help_"):
            return await cb_help(client, callback)
        elif query.startswith("cek_masa_aktif"):
            return await cek_expired_cb(client, callback)
        elif query.startswith("viewchord_"):
            return await viewchord(client, callback)
        elif query.startswith("viewgempa_"):
            return await viewgempa(client, callback)
        elif query.startswith("nxtbmkg_"):
            return await nxtbmkg(client, callback)
        elif query.startswith("planusers"):
            return await chose_plan(client, callback)
        elif query.startswith("alertcb_"):
            return await callback_alert(client, callback)
        elif query.startswith("an1cb_"):
            return await an1cb(client, callback)
        elif query.startswith("moddycb_"):
            return await moddycb(client, callback)
        elif query.startswith("calculatorcb_"):
            return await calculator_callback(client, callback)
        elif query.startswith("dlytsearch_"):
            return await dl_ytsearch(client, callback)
        elif query.startswith("nxtytsearch_"):
            return await nxt_ytsearch(client, callback)
        elif query.startswith("selectedtopic_"):
            return await selected_topic(client, callback)
    except Exception:
        logger.error(f"Callback error: {traceback.format_exc()}")
