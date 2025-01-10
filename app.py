import logging
from quart import Quart  # استيراد Quart لإنشاء تطبيق ويب
import asyncio
from config import port  # استيراد المنفذ من config.py

app = Quart(__name__)

# مهمة خلفية تعمل كل 2.5 دقيقة
async def background_worker():
    while True:
        logging.info("الخادم قيد التشغيل...")
        await asyncio.sleep(150)  # انتظار 2.5 دقيقة (150 ثانية)

@app.before_serving
async def startup():
    # بدء المهمة الخلفية عند بدء تشغيل التطبيق
    app.background_task = asyncio.create_task(background_worker())

@app.route('/')
async def home():
    logging.info("تم الوصول إلى الصفحة الرئيسية!")
    return "الخدمة قيد التشغيل!"

async def run_app():
    logging.info("جارٍ بدء تطبيق Quart...")
    await app.run_task(host='0.0.0.0', port=port)