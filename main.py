from fastapi import FastAPI, Request
from datetime import datetime, timedelta
import json
import os

app = FastAPI()
KEYS_FILE = "keys.json"
LOG_FILE = "logs.txt"

if os.path.exists(KEYS_FILE):
    with open(KEYS_FILE, "r") as f:
        keys_db = json.load(f)
else:
    keys_db = {
        "5FphhRQmyWWTRgMl5PfYQ": {"days": 7, "hwid": None, "activated": None},
        "oiGQTaSktgAmARQCdSxQo": {"days": 30, "hwid": None, "activated": None},
        "GFwlF6hsZ3eXu2NuZv2Zg": {"days": 999999, "hwid": None, "activated": None},
    }

def save_keys_db():
    with open(KEYS_FILE, "w") as f:
        json.dump(keys_db, f, indent=4)
    print(f"[{datetime.now()}] keys.json обновлён")

@app.post("/check_key")
async def check_key(request: Request):
    data = await request.json()
    key = data.get("license_key")
    hwid = data.get("hwid")
    now = datetime.now()

    if key not in keys_db:
        log = f"[{now}] ❌ Неверный ключ: {key}\n"
        with open(LOG_FILE, "a") as f:
            f.write(log)
        return {"status": "error", "message": "Неверный ключ"}

    key_data = keys_db[key]

    if key_data["hwid"]:
        if key_data["hwid"] != hwid:
            log = f"[{now}] ❌ HWID не совпадает: {key} | HWID: {hwid}\n"
            with open(LOG_FILE, "a") as f:
                f.write(log)
            return {"status": "error", "message": "Ключ уже используется на другом устройстве"}
        else:
            # Здесь можно обновлять дату последнего запроса, если хочешь
            save_keys_db()
    else:
        key_data["hwid"] = hwid
        key_data["activated"] = now.strftime("%Y-%m-%d %H:%M:%S")
        save_keys_db()

    activated = datetime.strptime(key_data["activated"], "%Y-%m-%d %H:%M:%S")
    expires = activated + timedelta(days=key_data["days"])
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
