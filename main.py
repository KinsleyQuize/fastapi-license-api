from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import os

app = FastAPI()

# Модель входных данных
class LicenseCheckRequest(BaseModel):
    license_key: str
    hwid: str

# Настройки подключения к БД из env или по умолчанию
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'wVAjqLiUofKWDLWS@2 '),
    'database': os.getenv('DB_NAME', 'licenses_db'),
}

def check_license_in_db(license_key: str, hwid: str):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT days_left FROM licenses
        WHERE license_key = %s AND hwid = %s AND days_left > 0
        """
        cursor.execute(query, (license_key, hwid))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            return result['days_left']
        return None
    except Exception as e:
        print(f"DB error: {e}")
        return None

@app.post("/check_key")
async def check_key(data: LicenseCheckRequest):
    days_left = check_license_in_db(data.license_key, data.hwid)
    if days_left is not None:
        return {"status": "success", "days_left": days_left}
    else:
        raise HTTPException(status_code=400, detail="Invalid license or no days left")
