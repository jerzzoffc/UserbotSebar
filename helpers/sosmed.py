import re
from typing import Optional

import httpx

from logs import logger

from .tools import Tools


class SocialMedia:
    def __init__(
        self, api_host: str = "social-download-all-in-one.p.rapidapi.com", api_key=str
    ):
        self.api_host = api_host
        self.api_key = api_key
        self.api_url = f"https://{api_host}/v1/social/autolink"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host,
            "Content-Type": "application/json",
        }

    async def download_media(self, link: str) -> Optional[dict]:
        payload = {"url": link}
        try:
            res = await Tools.fetch.post(
                self.api_url, json=payload, headers=self.headers
            )
            if res.status_code != 200:
                return None
            data = res.json()
            logger.info(f"Data Mentah: {data}")
        except Exception as e:
            logger.error(f"Gagal mengambil metadata: {e}")
            return None

        medias = data.get("medias", [])
        if not medias:
            logger.info(f"Data medias kosong: {data}")
            return None

        return medias

    @staticmethod
    def is_url(string: str) -> bool:
        url_pattern = re.compile(r"^(https?://[^\s]+)$", re.IGNORECASE)
        return bool(url_pattern.match(string.strip()))


class BtchDownloader:
    BASE_URL = "https://backend1.tioo.eu.org"
    __version__ = "4.0.15"
    HEADERS = {
        "Content-Type": "application/json",
        "User-Agent": "btch/4.0.15",
    }

    def __init__(self):
        self.platform_patterns = {
            "instagram": r"(https?://)?(www\.)?instagram\.com",
            "tiktok": r"(https?://)?(www\.)?tiktok\.com",
            "youtube": r"(https?://)?(www\.)?(youtube\.com|youtu\.be)",
            "twitter": r"(https?://)?(www\.)?(twitter\.com|x\.com)/",
            "facebook": r"(https?://)?(www\.)?facebook\.com",
            "mediafire": r"(https?://)?(www\.)?mediafire\.com",
            "capcut": r"(https?://)?(www\.)?capcut\.com",
            "gdrive": r"(https?://)?(drive\.google\.com)",
            "pinterest": r"(https?://)?(www\.)?pinterest\.com|pin\.it",
        }

    async def _fetch_api(self, endpoint, url):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/{endpoint}",
                    params={"url": url},
                    headers=self.HEADERS,
                    timeout=httpx.Timeout(15),
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as error:
                return {
                    "developer": "@LuciferReborns",
                    "status": False,
                    "message": f"Error fetching from {endpoint}: {str(error)}",
                }

    def _detect_platform(self, url):
        for platform, pattern in self.platform_patterns.items():
            if re.search(pattern, url):
                return platform
        return None

    async def download(self, url):
        platform = self._detect_platform(url)
        if not platform:
            return {
                "developer": "@LuciferReborns",
                "status": False,
                "message": "Unsupported or unrecognized URL platform.",
            }

        endpoint_map = {
            "instagram": "igdl",
            "tiktok": "ttdl",
            "youtube": "youtube",
            "twitter": "twitter",
            "facebook": "fbdown",
            "mediafire": "mediafire",
            "capcut": "capcut",
            "gdrive": "gdrive",
            "pinterest": "pinterest",
        }

        endpoint = endpoint_map.get(platform)
        data = await self._fetch_api(endpoint, url)

        if isinstance(data, list):
            return [
                {
                    "url": item.get("url"),
                    "thumbnail": item.get("thumbnail"),
                    "resolution": item.get("resolution"),
                }
                for item in data
            ]

        return data

    async def tiktok(self, url: str):
        try:
            data = await self._fetch_api("ttdl", url)
            return {
                "developer": "@LuciferReborns",
                "title": data.get("title"),
                "title_audio": data.get("title_audio"),
                "thumbnail": data.get("thumbnail"),
                "video": data.get("video"),
                "audio": data.get("audio"),
            }
        except Exception as e:
            return self._error("tiktok", e)

    async def instagram(self, url: str):
        try:
            data = await self._fetch_api("igdl", url)

            if not data or (isinstance(data, dict) and data.get("status") is False):
                return {
                    "developer": "@LuciferReborns",
                    "status": False,
                    "message": (
                        data.get("msg", "Result Not Found!")
                        if isinstance(data, dict)
                        else "Result Not Found!"
                    ),
                    "note": "See: https://github.com/hostinger-bot/btch-downloader-py",
                }

            if isinstance(data, list):
                return [
                    {
                        "developer": item.get("creator", "@LuciferReborns"),
                        "thumbnail": item.get("thumbnail"),
                        "url": item.get("url"),
                        "resolution": item.get("resolution", "unknown"),
                        "shouldRender": item.get("shouldRender", True),
                    }
                    for item in data
                ]

            return {
                "developer": "@LuciferReborns",
                "status": False,
                "message": "Invalid data format",
                "note": "See: https://github.com/hostinger-bot/btch-downloader-py",
            }
        except Exception as e:
            return self._error("instagram", e)

    async def twitter(self, url: str):
        try:
            data = await self._fetch_api("twitter", url)
            return {
                "developer": "@LuciferReborns",
                "title": data.get("title"),
                "url": data.get("url"),
            }
        except Exception as e:
            return self._error("twitter", e)

    async def youtube(self, url: str):
        try:
            data = await self._fetch_api("youtube", url)
            return {
                "developer": "@LuciferReborns",
                "title": data.get("title"),
                "thumbnail": data.get("thumbnail"),
                "author": data.get("author"),
                "mp3": data.get("mp3"),
                "mp4": data.get("mp4"),
            }
        except Exception as e:
            return self._error("youtube", e)

    async def facebook(self, url: str):
        try:
            data = await self._fetch_api("fbdown", url)
            return {
                "developer": "@LuciferReborns",
                "Normal_video": data.get("Normal_video"),
                "HD": data.get("HD"),
            }
        except Exception as e:
            return self._error("facebook", e)

    async def aio(self, url: str):
        try:
            data = await self._fetch_api("aio", url)
            return {"developer": "@LuciferReborns", "url": data.get("url")}
        except Exception as e:
            return self._error("aio", e)

    async def mediafire(self, url: str):
        try:
            data = await self._fetch_api("mediafire", url)
            return {"developer": "@LuciferReborns", "result": data}
        except Exception as e:
            return self._error("mediafire", e)

    async def capcut(self, url: str):
        try:
            data = await self._fetch_api("capcut", url)
            return {"developer": "@LuciferReborns", "result": data}
        except Exception as e:
            return self._error("capcut", e)

    async def gdrive(self, url: str):
        try:
            data = await self._fetch_api("gdrive", url)
            return {"developer": "@LuciferReborns", "result": data.get("data")}
        except Exception as e:
            return self._error("gdrive", e)

    async def pinterest(self, mdl: str):
        try:
            data = await self._fetch_api("pinterest", mdl)
            return {"developer": "@LuciferReborns", "result": data.get("result")}
        except Exception as e:
            return self._error("pinterest", e)

    def _error(self, platform: str, error: Exception):
        return {
            "developer": "@LuciferReborns",
            "status": False,
            "message": f"{platform} error: {str(error)}",
            "note": "See: https://github.com/hostinger-bot/btch-downloader-py",
        }


media_dl = BtchDownloader()
