import json
import random
import string
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aioshutil
import aiosqlite
import pytz

from config import DB_NAME

jakarta_timezone = pytz.timezone("Asia/Jakarta")
DB_PATH = f"./{DB_NAME}.db"
ENV_PATH = f"./.env"
BACKUP_TIME = datetime.now(jakarta_timezone)
BACKUP_PATH = f"./{DB_NAME}_backup_{BACKUP_TIME}.db"


class DatabaseClient:
    def __init__(self) -> None:
        self.db_path = Path(DB_PATH)
        self.env_path = Path(ENV_PATH)
        self.db_backup = f"{DB_PATH}_{BACKUP_TIME}"
        self.db_backup_format = "zip"
        self.temp_dir = self.db_path.parent / "./output"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.chconnect = {}

    async def initialize(self):
        """Initialize the database connection and tables"""
        await self.connect()
        await self._initialize_database()

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db_path, check_same_thread=False)

    async def _initialize_database(self):
        script = """
        CREATE TABLE IF NOT EXISTS user_prefixes (
            user_id INTEGER PRIMARY KEY,
            prefix TEXT
        );
        CREATE TABLE IF NOT EXISTS floods (
            gw INTEGER,
            user_id INTEGER,
            flood TEXT,
            PRIMARY KEY (gw, user_id)
        );
        CREATE TABLE IF NOT EXISTS variabel (
            _id INTEGER PRIMARY KEY,
            vars TEXT
        );
        CREATE TABLE IF NOT EXISTS expired (
            _id INTEGER PRIMARY KEY,
            expire_date TEXT
        );
        CREATE TABLE IF NOT EXISTS userdata (
            user_id INTEGER PRIMARY KEY,
            depan TEXT,
            belakang TEXT,
            username TEXT,
            mention TEXT,
            full TEXT,
            _id INTEGER
        );
        CREATE TABLE IF NOT EXISTS ubotdb (
            user_id TEXT PRIMARY KEY,
            session_string TEXT
        );
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            owner TEXT,
            created_at TEXT,
            usage_count INTEGER,
            max_usage INTEGER,
            usage_history TEXT
        );

        """
        await self.conn.executescript(script)
        await self.conn.commit()

    async def ensure_connection(self):
        if self.conn is None:
            await self.connect()

    async def get_pref(self, user_id):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT prefix FROM user_prefixes WHERE user_id = ?", (user_id,)
            )
            result = await cursor.fetchone()
            return json.loads(result[0]) if result else [".", "-", "!", "+", "?"]

    async def set_pref(self, user_id, prefix):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT OR REPLACE INTO user_prefixes (user_id, prefix)
                VALUES (?, ?)
            """,
                (user_id, json.dumps(prefix)),
            )
        await self.conn.commit()

    async def rem_pref(self, user_id):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM user_prefixes WHERE user_id = ?", (user_id,)
            )
        await self.conn.commit()

    async def set_var(self, bot_id, vars_name, value, query="vars"):
        await self.ensure_connection()
        json_value = json.dumps(value)
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT OR REPLACE INTO variabel (_id, vars)
                VALUES (?, json_set(COALESCE((SELECT vars FROM variabel WHERE _id = ?), '{}'), ?, ?))
                """,
                (bot_id, bot_id, f"$.{query}.{vars_name}", json_value),
            )
        await self.conn.commit()

    async def get_var(self, bot_id, vars_name, query="vars"):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT vars FROM variabel WHERE _id = ?", (bot_id,))
            document = await cursor.fetchone()

            if document:
                data = json.loads(document[0])
                value = data.get(query, {}).get(vars_name)
                try:
                    return json.loads(value) if isinstance(value, str) else value
                except json.JSONDecodeError:
                    return value
            return None

    async def remove_var(self, bot_id, vars_name, query="vars"):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE variabel SET vars = json_remove(vars, ?) WHERE _id = ?
            """,
                (f"$.{query}.{vars_name}", bot_id),
            )
        await self.conn.commit()

    async def all_var(self, user_id, query="vars"):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT vars FROM variabel WHERE _id = ?", (user_id,))
            result = await cursor.fetchone()
            return json.loads(result[0]).get(query) if result else None

    async def rm_all(self, bot_id):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute("DELETE FROM variabel WHERE _id = ?", (bot_id,))
        await self.conn.commit()

    async def get_list_from_var(self, user_id, vars_name, query="vars"):
        await self.ensure_connection()
        vars_data = await self.get_var(user_id, vars_name, query)
        return [int(x) for x in str(vars_data).split()] if vars_data else []

    async def add_to_var(self, user_id, vars_name, value, query="vars"):
        await self.ensure_connection()
        vars_list = await self.get_list_from_var(user_id, vars_name, query)
        vars_list.append(value)
        await self.set_var(user_id, vars_name, " ".join(map(str, vars_list)), query)

    async def remove_from_var(self, user_id, vars_name, value, query="vars"):
        await self.ensure_connection()
        vars_list = await self.get_list_from_var(user_id, vars_name, query)
        if value in vars_list:
            vars_list.remove(value)
            await self.set_var(user_id, vars_name, " ".join(map(str, vars_list)), query)

    async def get_expired_date(self, user_id):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT expire_date FROM expired WHERE _id = ?", (user_id,)
            )
            result = await cursor.fetchone()
            return (
                datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S.%f%z")
                if result and result[0]
                else None
            )

    async def set_expired_date(self, user_id, expire_date):
        if isinstance(expire_date, str):
            try:
                expire_date = datetime.strptime(expire_date, "%Y-%m-%d %H:%M:%S.%f%z")
            except ValueError:
                expire_date = datetime.strptime(expire_date, "%Y-%m-%d %H:%M:%S.%f")
                expire_date = expire_date.replace(tzinfo=timezone(timedelta(hours=7)))

        formatted_date = expire_date.strftime("%Y-%m-%d %H:%M:%S.%f%z")

        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT OR REPLACE INTO expired (_id, expire_date) VALUES (?, ?)
                """,
                (user_id, formatted_date),
            )
        await self.conn.commit()

    async def rem_expired_date(self, user_id):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE expired SET expire_date = NULL WHERE _id = ?
            """,
                (user_id,),
            )
        await self.conn.commit()

    async def cek_userdata(self, user_id: int) -> bool:
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT 1 FROM userdata WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()
            return bool(result)

    async def get_userdata(self, user_id: int):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM userdata WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()

            if result:
                return {
                    "user_id": result[0],
                    "depan": result[1],
                    "belakang": result[2],
                    "username": result[3],
                    "mention": result[4],
                    "full": result[5],
                    "_id": result[6],
                }
            return None

    async def add_userdata(
        self, user_id: int, depan, belakang, username, mention, full, _id
    ):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT OR REPLACE INTO userdata (user_id, depan, belakang, username, mention, full, _id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (user_id, depan, belakang, username, mention, full, _id),
            )
        await self.conn.commit()

    async def add_ubot(self, user_id, session_string):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT OR REPLACE INTO ubotdb (user_id, session_string)
                VALUES (?, ?)
                """,
                (user_id, session_string),
            )
        await self.conn.commit()

    async def remove_columns_ubotdb(self):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                """
                CREATE TABLE new_ubotdb (
                    user_id INTEGER PRIMARY KEY,
                    session_string TEXT NOT NULL
                )
            """
            )
            await cursor.execute(
                """
                INSERT INTO new_ubotdb (user_id, session_string)
                SELECT user_id, session_string FROM ubotdb
            """
            )
            await cursor.execute("DROP TABLE ubotdb")
            await cursor.execute("ALTER TABLE new_ubotdb RENAME TO ubotdb")
        await self.conn.commit()

    async def remove_ubot(self, user_id):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute("DELETE FROM ubotdb WHERE user_id = ?", (user_id,))
        await self.conn.commit()

    async def get_ubot(self, user_id):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT user_id, session_string FROM ubotdb WHERE user_id = ?",
                (user_id,),
            )
            row = await cursor.fetchone()
            if row:
                user_id, session_string = row
                return {
                    "name": str(user_id),
                    "session_string": session_string,
                }
            else:
                return None

    async def get_userbots(self):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT user_id, session_string FROM ubotdb WHERE user_id IS NOT NULL"
            )
            rows = await cursor.fetchall()
            return [
                {
                    "name": str(user_id),
                    "session_string": session_string,
                }
                for user_id, session_string in rows
            ]

    async def get_flood(self, gw: int, user_id: int):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT flood FROM floods WHERE gw = ? AND user_id = ?", (gw, user_id)
            )
            result = await cursor.fetchone()
            return result[0] if result else None

    async def set_flood(self, gw: int, user_id: int, flood: str):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT OR REPLACE INTO floods (gw, user_id, flood)
                VALUES (?, ?, ?)
            """,
                (gw, user_id, flood),
            )
        await self.conn.commit()

    async def remove_all_deleted_vars(self):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT _id FROM variabel")
            ids = await cursor.fetchall()
            for (_id,) in ids:
                await cursor.execute(
                    "UPDATE variabel SET vars = json_remove(vars, '$.vars.DELETED') WHERE _id = ?",
                    (_id,),
                )

        await self.conn.commit()

    async def rem_flood(self, gw: int, user_id: int):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM floods WHERE gw = ? AND user_id = ?", (gw, user_id)
            )
        await self.conn.commit()

    async def generate_token(
        self, user_id: str, length=16, group_size=4, separator="-"
    ) -> str:
        await self.ensure_connection()
        characters = string.ascii_uppercase + string.digits
        raw_token = "".join(random.choice(characters) for _ in range(length))
        grouped_token = separator.join(
            raw_token[i : i + group_size] for i in range(0, length, group_size)
        )
        clean_token = grouped_token.replace(separator, "")

        async with self.conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO tokens (token, owner, created_at, usage_count, max_usage, usage_history)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    clean_token,
                    user_id,
                    datetime.now().isoformat(),
                    0,
                    3,
                    json.dumps([]),
                ),
            )
        await self.conn.commit()
        return grouped_token

    async def get_token(self, user_id: int):
        await self.ensure_connection()
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT token, usage_count, max_usage FROM tokens WHERE owner = ?",
                (str(user_id),),
            )
            row = await cursor.fetchone()
            if not row:
                return None
            token, usage_count, max_usage = row
            grouped_token = "-".join(token[i : i + 4] for i in range(0, len(token), 4))
            return {
                "token": grouped_token,
                "usage_count": usage_count,
                "max_usage": max_usage,
                "remaining_usage": max_usage - usage_count,
            }

    async def revoke_token(self, user_id: int, deleted: bool = False):
        await self.ensure_connection()

        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT COUNT(*) FROM ubotdb WHERE user_id = ?", (user_id,)
            )
            count = await cursor.fetchone()
            if count[0] == 0:
                async with self.conn.cursor() as cursor2:
                    await cursor2.execute(
                        "DELETE FROM tokens WHERE owner = ?", (str(user_id),)
                    )
                await self.conn.commit()
                return False, "Token dihapus karena userbot tidak ditemukan."

        if deleted:
            async with self.conn.cursor() as cursor:
                await cursor.execute(
                    "DELETE FROM tokens WHERE owner = ?", (str(user_id),)
                )
            await self.conn.commit()
            return True, "Token berhasil dihapus."

        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT token, usage_count, max_usage, usage_history FROM tokens WHERE owner = ?",
                (str(user_id),),
            )
            row = await cursor.fetchone()
            if not row:
                return False, "Token lama tidak ditemukan."

            old_token, usage_count, max_usage, usage_history = row

            await cursor.execute("DELETE FROM tokens WHERE token = ?", (old_token,))
            await self.conn.commit()

        length = 16
        group_size = 4
        separator = "-"
        characters = string.ascii_uppercase + string.digits
        raw_token = "".join(random.choice(characters) for _ in range(length))
        grouped_token = separator.join(
            raw_token[i : i + group_size] for i in range(0, length, group_size)
        )
        clean_token = grouped_token.replace(separator, "")
        remaining_usage = max_usage - usage_count

        async with self.conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO tokens (token, owner, created_at, usage_count, max_usage, usage_history)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    clean_token,
                    str(user_id),
                    datetime.now().isoformat(),
                    usage_count,
                    max_usage,
                    usage_history,
                ),
            )
        await self.conn.commit()
        return (
            True,
            f"Token berhasil di-revoke dan diganti.\nToken baru: `{grouped_token}`\nSisa penggunaan: {remaining_usage}",
        )

    async def check_token_usage(self, token: str) -> dict:
        await self.ensure_connection()
        clean_token = token.replace("-", "")
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT owner, created_at, usage_count, max_usage, usage_history FROM tokens WHERE token = ?",
                (clean_token,),
            )
            row = await cursor.fetchone()
            if not row:
                return {
                    "valid": False,
                    "message": "Token tidak valid",
                    "usage_count": 0,
                    "max_usage": 3,
                    "remaining_usage": 0,
                }
            owner, created_at, usage_count, max_usage, usage_history = row
            return {
                "valid": True,
                "message": "Token valid",
                "usage_count": usage_count,
                "max_usage": max_usage,
                "remaining_usage": max_usage - usage_count,
                "owner": owner,
                "created_at": created_at,
                "usage_history": json.loads(usage_history),
            }

    async def use_token(self, token: str, usage_description: str = "Token digunakan"):
        await self.ensure_connection()
        clean_token = token.replace("-", "")
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT usage_count, max_usage, usage_history FROM tokens WHERE token = ?",
                (clean_token,),
            )
            row = await cursor.fetchone()
            if not row:
                return False, "Token tidak valid"
            usage_count, max_usage, usage_history = row
            if usage_count >= max_usage:
                return (
                    False,
                    f"Token telah mencapai batas penggunaan maksimal ({max_usage} kali)",
                )
            usage_count += 1
            history = json.loads(usage_history)
            history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "description": usage_description,
                }
            )
            await cursor.execute(
                """
                UPDATE tokens SET usage_count = ?, usage_history = ?
                WHERE token = ?
            """,
                (usage_count, json.dumps(history), clean_token),
            )
        await self.conn.commit()
        return (
            True,
            f"Token berhasil digunakan. Sisa penggunaan: {max_usage - usage_count} kali",
        )

    async def verify_token(self, token: str):
        await self.ensure_connection()
        clean_token = token.replace("-", "")
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT owner, usage_count, max_usage FROM tokens WHERE token = ?",
                (clean_token,),
            )
            row = await cursor.fetchone()
            if not row:
                return None
            owner, usage_count, max_usage = row
            if usage_count >= max_usage:
                return None
            return {"user_id": owner, "token": clean_token}

    async def backup_database(self):
        db_file = Path(self.db_path)
        env_file = Path(self.env_path)
        if not db_file.exists():
            print(f"⚠️ File {self.db_path} tidak ditemukan!")
            return None
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        temp_db_file = self.temp_dir / db_file.name
        if env_file.exists():
            await aioshutil.copy(env_file, temp_db_file)
            await aioshutil.copy(db_file, temp_db_file)
        else:
            await aioshutil.copy(db_file, temp_db_file)
        archive_full_path = await aioshutil.make_archive(
            self.db_backup, self.db_backup_format, self.temp_dir
        )
        await aioshutil.rmtree(self.temp_dir)
        print(f"✅ Arsip berhasil dibuat: {archive_full_path}")
        return archive_full_path

    async def close(self):
        if self.conn:
            await self.conn.close()
            print("Database connection closed.")


# Initialize database
dB = DatabaseClient()
