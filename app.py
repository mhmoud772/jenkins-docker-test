import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
import psycopg2
from psycopg2 import OperationalError

# 1. إعدادات التسجيل (Logs)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("VisitorLogger")

app = Flask(__name__)

class Config:
    DB_HOST = os.getenv('DB_HOST', 'my-db')
    DB_NAME = os.getenv('DB_NAME', 'mydb')
    DB_USER = os.getenv('DB_USER', 'myuser')
    DB_PASS = os.getenv('DB_PASS', 'supersecretpassword')
    DB_PORT = os.getenv('DB_PORT', '5432')

def get_db_connection():
    try:
        return psycopg2.connect(host=Config.DB_HOST, database=Config.DB_NAME, user=Config.DB_USER, password=Config.DB_PASS, port=Config.DB_PORT, connect_timeout=3)
    except OperationalError as e:
        logger.error(f"❌ DB Error: {e}")
        return None

# 2. إنشاء الجدول (نقطة هامة لمسار الـ DevOps)
def init_db():
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS visitor_logs (
                    id SERIAL PRIMARY KEY,
                    visitor_ip TEXT NOT NULL,
                    visit_time TIMESTAMP NOT NULL
                );
            ''')
            conn.commit()
        conn.close()
        logger.info("✅ Database Table Initialized")

# 3. قالب Bootstrap المطور لعرض جدول الزوار
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><title>Visitor Monitoring</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="card shadow-sm">
            <div class="card-body text-center">
                <h2 class="text-primary mb-4">🚀 Infrastructure Visitor Logs</h2>
                
                <div class="table-responsive mt-4 text-start">
                    <table class="table table-hover table-striped border">
                        <thead class="table-dark">
                            <tr>
                                <th># ID</th>
                                <th>Visitor IP</th>
                                <th>Visit Timestamp</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for visitor in visitors %}
                            <tr>
                                <td>{{ visitor[0] }}</td>
                                <td><span class="badge bg-info text-dark">{{ visitor[1] }}</span></td>
                                <td>{{ visitor[2].strftime('%Y-%m-%d %H:%M:%S') }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                <button class="btn btn-primary mt-3" onclick="location.reload()">New Visit / Refresh</button>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    init_db() # التأكد من وجود الجدول عند كل دخول (أو عند بدء التطبيق)
    conn = get_db_connection()
    if not conn: return "<h1>DB Connection Error</h1>", 500

    try:
        with conn.cursor() as cur:
            # تسجيل الزيارة الحالية
            visitor_ip = request.remote_addr
            cur.execute("INSERT INTO visitor_logs (visitor_ip, visit_time) VALUES (%s, %s)", (visitor_ip, datetime.now()))
            
            # جلب آخر 10 زوار
            cur.execute("SELECT id, visitor_ip, visit_time FROM visitor_logs ORDER BY id DESC LIMIT 10")
            visitors = cur.fetchall()
            conn.commit()
            return render_template_string(HTML_TEMPLATE, visitors=visitors)
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
