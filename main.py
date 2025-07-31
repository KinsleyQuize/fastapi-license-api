from fastapi import FastAPI, Request
from datetime import datetime, timedelta
import asyncpg
import asyncio
import os

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://license_db_hjw3_user:oDtnt6T5oqlyAxjOfiemgMFQAzARkoBx@dpg-d25r703e5dus73abmra0-a.postgres.render.com/license_db_hjw3?sslmode=require"

LOG_FILE = "logs.txt"

# Инициализация подключения к базе (будет создана при старте)
db_pool = None

async def insert_initial_licenses():
    keys = [
        ("5FphhRQmyWWTRgMl5PfYQ", 7),
        ("oiGQTaSktgAmARQCdSxQo", 30),
        ("GFwlF6hsZ3eXu2NuZv2Zg", 999999),
    ]
    async with db_pool.acquire() as conn:
        for key, days in keys:
            exists = await conn.fetchval("SELECT 1 FROM licenses WHERE license_key=$1", key)
            if not exists:
                await conn.execute(
                    "INSERT INTO licenses (license_key, days, hwid, activated) VALUES ($1, $2, NULL, NULL)",
                    key, days
                )
        print("[INFO] Initial license keys inserted or already exist.")

@app.on_event("startup")
async def startup():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    await insert_initial_licenses()

@app.on_event("shutdown")
async def shutdown():
    await db_pool.close()

@app.post("/check_key")
async def check_key(request: Request):
    data = await request.json()
    key = data.get("license_key")
    hwid = data.get("hwid")
    now = datetime.now()

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM licenses WHERE license_key=$1", key)

        if not row:
            log = f"[{now}] ❌ Неверный ключ: {key}\n"
            with open(LOG_FILE, "a") as f:
                f.write(log)
            return {"status": "error", "message": "Неверный ключ"}

        # Проверка HWID
        db_hwid = row["hwid"]
        activated = row["activated"]
        days = row["days"]

        if db_hwid:
            if db_hwid != hwid:
                log = f"[{now}] ❌ HWID не совпадает: {key} | HWID: {hwid}\n"
                with open(LOG_FILE, "a") as f:
                    f.write(log)
                return {"status": "error", "message": "Ключ уже используется на другом устройстве"}
        else:
            # Привязываем HWID и дату активации
            activated_str = now.strftime("%Y-%m-%d %H:%M:%S")
            await conn.execute(
                "UPDATE licenses SET hwid=$1, activated=$2 WHERE license_key=$3",
                hwid, activated_str, key
            )
            activated = now

        if isinstance(activated, str):
            activated = datetime.strptime(activated, "%Y-%m-%d %H:%M:%S")

        expires = activated + timedelta(days=days)
        days_left = (expires - now).days

        if now > expires:
            log = f"[{now}] ❌ Ключ просрочен: {key} | HWID: {hwid}\n"
            with open(LOG_FILE, "a") as f:
                f.write(log)
            return {"status": "error", "message": "Срок действия ключа истёк"}

        log = f"[{now}] ✅ Успешная активация: {key} | HWID: {hwid} | Осталось дней: {days_left}\n"
        with open(LOG_FILE, "a") as f:
            f.write(log)

        return {"status": "success", "days_left": days_left}
