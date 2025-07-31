import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI

app = FastAPI()

DB_HOST = "dpg-d25r703e5dus73abmra0-a.postgres.render.com"
DB_PORT = 5432
DB_NAME = "license_db_hjw3"
DB_USER = "license_db_hjw3_user"
DB_PASSWORD = "oDtnt6T5oqlyAxjOfiemgMFQAzARkoBx"

def insert_initial_licenses():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require"
    )
    cur = conn.cursor()

    keys_to_insert = [
        ("5FphhRQmyWWTRgMl5PfYQ", 7),
        ("oiGQTaSktgAmARQCdSxQo", 30),
        ("GFwlF6hsZ3eXu2NuZv2Zg", 999999)
    ]

    for license_key, days in keys_to_insert:
        cur.execute("SELECT 1 FROM licenses WHERE license_key = %s", (license_key,))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO licenses (license_key, days, hwid, activated)
                VALUES (%s, %s, NULL, NULL)
            """, (license_key, days))
            print(f"[+] Ключ {license_key} добавлен в базу данных")

    conn.commit()
    cur.close()
    conn.close()

@app.on_event("startup")
def startup_event():
    insert_initial_licenses()
    print("[*] Начальные лицензионные ключи проверены и добавлены при необходимости")

@app.get("/")
def read_root():
    return {"status": "Server is running"}

# Добавь сюда свои остальные эндпоинты по необходимости
