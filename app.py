from flask import Flask, request, jsonify
import psycopg2
import os
import sys
import logging

# --- 1. إعدادات نظام التسجيل (Logging) ---
# كمهندس DevOps، السجلات هي عينك داخل الحاوية
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- 2. جلب الإعدادات من متغيرات البيئة (Environment Variables) ---
DB_HOST = os.getenv('DB_HOST', 'my-db')
DB_NAME = os.getenv('DB_NAME', 'mydb')
DB_USER = os.getenv('DB_USER', 'myuser')
DB_PASS = os.getenv('DB_PASS', 'supersecretpassword')

DB_CONFIG = {
    "host": DB_HOST,
    "database": DB_NAME,
    "user": DB_USER,
    "password": DB_PASS,
    "connect_timeout": 5
}

def get_db_connection():
    """وظيفة لإنشاء اتصال بقاعدة البيانات مع معالجة الأخطاء"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"❌ Failed to connect to Postgres: {e}")
        return None

# --- 3. المسارات (Routes) ---

@app.route('/')
def index():
    """المسار الرئيسي لعرض حالة الاتصال"""
    conn = get_db_connection()
    if conn:
        logger.info("✅ Connection successful to Database")
        cur = conn.cursor()
        cur.execute('SELECT version();')
        db_version = cur.fetchone()
        cur.close()
        conn.close()
        return f"<h1>Docker Infrastructure Active!</h1><p>Connected to: {db_version[0]}</p>"
    else:
        return "<h1>Infrastructure Error</h1><p>Could not connect to database.</p>", 500

@app.route('/health')
def health_check():
    """مسار مخصص لـ Docker Healthcheck ليتأكد أن التطبيق حي"""
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify(status="healthy"), 200
    else:
        return jsonify(status="unhealthy"), 500

# --- 4. تشغيل التطبيق ---
if __name__ == "__main__":
    logger.info("🚀 Starting Flask App on port 80...")
    # الاستماع على 0.0.0.0 ضروري داخل دوكر ليتمكن السيرفر من الوصول للحاوية
    app.run(host="0.0.0.0", port=80)
