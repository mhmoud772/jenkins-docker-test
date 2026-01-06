# استخدام نسخة بايثون خفيفة
FROM python:3.9-slim

# تثبيت مكتبات النظام اللازمة لربط Postgres
RUN apt-get update && apt-get install -y libpq-dev gcc

# تحديد مجلد العمل
WORKDIR /app

# تثبيت Flask ومكتبة الاتصال بقاعدة البيانات
RUN pip install flask psycopg2-binary

# نسخ كود التطبيق
COPY app.py .

# تشغيل التطبيق
CMD ["python", "app.py"]
