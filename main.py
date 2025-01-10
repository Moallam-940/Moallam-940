import asyncio
import logging
from bot_handler import handle_bot  # استيراد دالة handle_bot من bot_handler.py
from app import run_app  # استيراد دالة run_app من app.py

# تهيئة السجل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    logging.info("جارٍ بدء خدمة البوت...")

    # إنشاء المهام للتعامل مع البوتات
    task1 = asyncio.create_task(handle_bot("Bitcoin (BTC) Cloud Pool", "Get Coin 🎁", "🎁 Daily Bonus 🎁"))
    task2 = asyncio.create_task(handle_bot("Daily (USDT) Claim", "🆔 Account Balance", "🔥 Huge Extra Bonus 🔥"))

    # تشغيل تطبيق Quart
    await run_app()

    # انتظار انتهاء المهام
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    logging.info("جارٍ تهيئة التطبيق...")
    asyncio.run(main())