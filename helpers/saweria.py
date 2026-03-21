import asyncio
import io
import json
import os
import random
import re
from typing import Optional, Tuple

import aiofiles
import cloudscraper25 as cloudscraper
import qrcode
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont


class SaweriaScraper:
    BACKEND = "https://backend.saweria.co"
    FRONTEND = "https://saweria.co"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }

    RANDOM_MESSAGES = [
        "Semangat kak!",
        "Terima kasih atas kontennya",
        "Lanjutkan karya baiknya",
        "Support terus",
        "Keep up the good work!",
        "Sukses selalu",
        "Tetap semangat",
    ]

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    @staticmethod
    def random_sender() -> str:
        names = [
            "Budi",
            "Ani",
            "Dedi",
            "Rina",
            "Joko",
            "Siti",
            "Ahmad",
            "Dewi",
            "Agus",
            "Linda",
            "Rudi",
            "Maya",
            "Fajar",
            "Nina",
            "Hendra",
            "Lina",
            "Yanto",
            "Bayu",
            "Dina",
            "Rizky",
            "Sari",
            "Aji",
            "Rita",
            "Doni",
            "Wati",
            "Irfan",
            "Yuni",
            "Rama",
            "Dewi",
        ]
        return random.choice(names)

    @staticmethod
    def random_message() -> str:
        return random.choice(SaweriaScraper.RANDOM_MESSAGES)

    @staticmethod
    def insert_plus_in_email(email: str, insert_str: str) -> str:
        return email.replace("@", f"+{insert_str}@", 1)

    async def get_user_id_debug(self, username: str):
        def _sync_get():
            url = f"https://saweria.co/{username}"
            res = self.scraper.get(url)
            return res.status_code, res.text

        status, html = await asyncio.to_thread(_sync_get)
        print(status, html[:200])  # Debug

    async def get_user_id(self, username: str) -> Optional[str]:
        if not username or not isinstance(username, str):
            raise ValueError("Username harus berupa string dan tidak boleh kosong.")

        def _sync_get():
            url = f"{self.FRONTEND}/{username}"
            res = self.scraper.get(url)
            if res.status_code != 200:
                return None

            soup = BeautifulSoup(res.text, "html.parser")
            next_data = soup.find(id="__NEXT_DATA__")
            if not next_data:
                return None

            try:
                data = json.loads(next_data.text)
                # print(f"Data: {data}")
                user_id = (
                    data.get("props", {}).get("pageProps", {}).get("data", {}).get("id")
                )
                print(f"Saweria UserID: {user_id}")
            except Exception:
                return None

            if not user_id:
                return None
            return user_id

        return await asyncio.to_thread(_sync_get)

    async def create_payment_qr(
        self,
        user_id: str,
        saweria_username: str,
        amount: int,
        email: str,
        output_path: str = "qris.png",
        use_template: bool = True,
    ) -> Tuple[str, str, str]:
        if not saweria_username or not amount or not email:
            raise ValueError("Parameter is missing!")
        if amount < 1000:
            raise ValueError("Minimum amount is 1000")
        await asyncio.sleep(5)
        sender = self.random_sender()
        message = self.random_message()
        email_plus = self.insert_plus_in_email(email, sender)
        payload = {
            "agree": True,
            "notUnderage": True,
            "message": message,
            "amount": amount,
            "payment_type": "qris",
            "vote": "",
            "currency": "IDR",
            "customer_info": {"first_name": sender, "email": email_plus, "phone": ""},
        }

        def _sync_post():
            res = self.scraper.post(
                f"{self.BACKEND}/donations/{user_id}",
                json=payload,
                headers=self.HEADERS,
            )
            if not res.ok:
                raise Exception(f"Failed to create payment: {res.text}")
            return res.json()["data"]

        data = await asyncio.to_thread(_sync_post)
        qr_string = data["qr_string"]
        transaction_id = data["id"]

        await self.generate_qr_image(
            qr_string, output_path, saweria_username if use_template else None
        )

        return qr_string, transaction_id, output_path

    async def check_paid_status(self, transaction_id: str) -> bool:
        def _sync_get():
            res = self.scraper.get(
                f"{self.BACKEND}/donations/qris/{transaction_id}", headers=self.HEADERS
            )
            if not res.ok:
                raise Exception("Transaction ID not found")
            return res.json()["data"]["qr_string"] == ""

        return await asyncio.to_thread(_sync_get)

    @staticmethod
    def get_amount(qr_text: str):
        match = re.search(r"54(\d{2})(\d+)", qr_text)
        if not match:
            return None
        length = int(match.group(1))
        value = match.group(2)[:length]
        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
    def draw_letter_spacing(
        draw,
        text,
        position,
        font,
        fill="black",
        spacing=2,
        anchor="mm",
        stroke_width=0,
        stroke_fill=None,
    ):
        x, y = position
        total_width = sum(font.getlength(char) + spacing for char in text) - spacing

        if anchor == "mm":
            x -= total_width / 2

        for char in text:
            if stroke_width > 0 and stroke_fill:
                draw.text(
                    (x, y),
                    char,
                    font=font,
                    fill=stroke_fill,
                    stroke_width=stroke_width,
                    stroke_fill=stroke_fill,
                )
            draw.text((x, y), char, font=font, fill=fill)
            x += font.getlength(char) + spacing

    async def generate_qr_image(
        self,
        qr_string: str,
        output_path: str = "qris.png",
        saweria_username: Optional[str] = None,
    ):
        template_path = "storage/cache/template_qris.png"
        img = Image.open(template_path).convert("RGBA")
        width_qr = int(img.width * 270 / 517)
        qr_img = qrcode.make(qr_string).resize((width_qr, width_qr)).convert("RGBA")

        if saweria_username and os.path.exists(template_path):
            template = Image.open(template_path).convert("RGBA")
            qr_img_size = int(template.width * 270 / 517)
            qr_img = qr_img.resize((qr_img_size, qr_img_size))

            x = (template.width - qr_img_size) // 2
            y = int(template.height * 0.4) - int((qr_img.height // 2) + 80)

            template.paste(qr_img, (x, y), mask=qr_img)
            draw = ImageDraw.Draw(template)
            try:
                font = ImageFont.truetype("arialbd.ttf", 72)
            except Exception:
                font = ImageFont.load_default()
            x_potition = template.width // 2
            y_potition = int(template.height * 0.2) - int((qr_img.height // 2) + 80)
            position = (x_potition, y_potition)

            self.draw_letter_spacing(
                draw=draw,
                text=saweria_username,
                position=(position[0] + 1, position[1] + 1),
                font=font,
                fill="black",
                spacing=2,
                anchor="mm",
            )

            self.draw_letter_spacing(
                draw=draw,
                text=saweria_username,
                position=position,
                font=font,
                fill="white",
                spacing=2,
                anchor="mm",
                stroke_width=3,
            )

            buffer = io.BytesIO()
            template.save(buffer, format="PNG")
            buffer.seek(0)
            folder_path = os.path.dirname(output_path)
            os.makedirs(folder_path, exist_ok=True)
            async with aiofiles.open(output_path, "wb") as f:
                await f.write(buffer.read())
        else:
            buffer = io.BytesIO()
            qr_img.save(buffer, format="PNG")
            buffer.seek(0)
            folder_path = os.path.dirname(output_path)
            os.makedirs(folder_path, exist_ok=True)
            async with aiofiles.open(output_path, "wb") as f:
                await f.write(buffer.read())

    def close(self):
        pass


Saweria = SaweriaScraper()
