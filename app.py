from flask import Flask, request
import psycopg2
from datetime import datetime
import os

app = Flask(__name__)

# إعدادات الاتصال
DB_CONFIG = {
    "host": "my-db",
    "database": "mydb",
    "user": "user",
    "password": "password"
}

def init_db():
    """إنشاء الجدول إذا لم يكن موجوداً"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id SERIAL PRIMARY KEY,
            visitor_ip TEXT,
            visit_time TIMESTAMP
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def hello():
    init_db() # التأكد من وجود الجدول
    
    # حفظ الزيارة الحالية
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("INSERT INTO visits (visitor_ip, visit_time) VALUES (%s, %s)", 
                (request.remote_addr, datetime.now()))
    
    # جلب آخر 5 زيارات
    cur.execute("SELECT visitor_ip, visit_time FROM visits ORDER BY visit_time DESC LIMIT 5")
    rows = cur.fetchall()
    
    conn.commit()
    cur.close()
    conn.close()

    # تنسيق النتيجة للعرض
    html = "<h1>Welcome! Python & Postgres are working!</h1>"
    html += "<h3>Recent Visitors:</h3><ul>"
    for row in rows:
        html += f"<li>IP: {row[0]} | Time: {row[1]}</li>"
    html += "</ul>"
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
