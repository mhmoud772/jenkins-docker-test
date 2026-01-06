import os
import sys
import logging
from flask import Flask, request, jsonify, render_template_string
import psycopg2
from psycopg2 import OperationalError

# 1. إعدادات التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DevOpsApp")

app = Flask(__name__)

# 2. الإعدادات
class Config:
    DB_HOST = os.getenv('DB_HOST', 'my-db')
    DB_NAME = os.getenv('DB_NAME', 'mydb')
    DB_USER = os.getenv('DB_USER', 'myuser')
    DB_PASS = os.getenv('DB_PASS', 'supersecretpassword')
    DB_PORT = os.getenv('DB_PORT', '5432')

# 3. وظيفة الاتصال
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            port=Config.DB_PORT,
            connect_timeout=3
        )
        return conn
    except OperationalError as e:
        logger.error(f"❌ DB Connection Error: {e}")
        return None

# 4. قوالب Bootstrap (HTML Template)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Infrastructure</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .hero-card { border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .status-dot { height: 12px; width: 12px; border-radius: 50%; display: inline-block; }
    </style>
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card hero-card border-0">
                    <div class="card-body p-5 text-center">
                        <h1 class="display-5 fw-bold text-primary mb-4">🚀 Docker Infrastructure</h1>
                        
                        <div class="alert {{ alert_class }} d-flex align-items-center justify-content-center py-3" role="alert">
                            <span class="status-dot me-2 {{ dot_class }}"></span>
                            <strong class="fs-5">{{ status_text }}</strong>
                        </div>

                        <div class="mt-4 text-start">
                            <h5 class="text-secondary border-bottom pb-2">Technical Details</h5>
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Database Host:</span>
                                    <span class="badge bg-dark text-white">{{ db_host }}</span>
                                </li>
                                <li class="list-group-item">
                                    <small class="text-muted"><strong>Version:</strong> {{ db_version }}</small>
                                </li>
                            </ul>
                        </div>
                        
                        <div class="mt-5">
                            <button class="btn btn-outline-primary btn-sm" onclick="location.reload()">Refresh State</button>
                        </div>
                    </div>
                </div>
                <p class="text-center mt-4 text-muted small">DevOps Pipeline v2.0 | Managed by Jenkins & Docker</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

# 5. المسارات
@app.route('/')
def index():
    conn = get_db_connection()
    if not conn:
        return render_template_string(HTML_TEMPLATE, 
            alert_class="alert-danger", dot_class="bg-danger",
            status_text="Infrastructure Error: Connection Failed",
            db_host=Config.DB_HOST, db_version="N/A"), 500

    try:
        with conn.cursor() as cur:
            cur.execute('SELECT version();')
            version = cur.fetchone()[0]
            return render_template_string(HTML_TEMPLATE, 
                alert_class="alert-success", dot_class="bg-success",
                status_text="System Active & Connected",
                db_host=Config.DB_HOST, db_version=version)
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
