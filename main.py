from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Подключение к базе — берем параметры из переменных окружения Render
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'wVAjqLiUofKWDLWS@2 '),
    'database': os.getenv('DB_NAME', 'license_system'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/check_key', methods=['POST'])
def check_key():
    data = request.json
    license_key = data.get('license_key')
    hwid = data.get('hwid')

    if not license_key:
        return jsonify({'error': 'license_key required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM licenses WHERE license_key = %s", (license_key,))
    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        return jsonify({'valid': False, 'message': 'Invalid license key'}), 404

    activated_at = row['activated_at']
    days = row['days']

    if activated_at:
        expired_at = activated_at + timedelta(days=days)
        if datetime.utcnow() > expired_at:
            cursor.close()
            conn.close()
            return jsonify({'valid': False, 'message': 'License expired'}), 403

    if not row['hwid'] and hwid:
        cursor.execute(
            "UPDATE licenses SET hwid = %s, activated_at = %s WHERE license_key = %s",
            (hwid, datetime.utcnow(), license_key)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'valid': True, 'message': 'Activated successfully'})

    if row['hwid'] and row['hwid'] != hwid:
        cursor.close()
        conn.close()
        return jsonify({'valid': False, 'message': 'HWID mismatch'}), 403

    cursor.close()
    conn.close()
    return jsonify({'valid': True, 'message': 'License valid'})

if __name__ == '__main__':
    # Для Render нужно использовать порт из переменной окружения
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
