from flask import Flask
import psycopg2
import os

app = Flask(__name__)

# جلب بيانات الاتصال من متغيرات البيئة (أفضل ممارسة في دوكر)
DB_HOST = "my-db" # اسم الخدمة في docker-compose
DB_NAME = "mydb"
DB_USER = "user"
DB_PASS = "password"

@app.route('/')
def hello():
    try:
        # محاولة الاتصال بقاعدة البيانات
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
        )
        cur = conn.cursor()
        cur.execute('SELECT version();')
        db_version = cur.fetchone()
        cur.close()
        conn.close()
        return f"<h1>Python connected to Postgres!</h1><p>DB Version: {db_version}</p>"
    except Exception as e:
        return f"<h1>Error!</h1><p>{str(e)}</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
