import asyncio
import logging
from telegram_client import client  # استيراد العميل من telegram_client.py
from bot_handler import handle_bot
from app import run_app
from config import port  # استيراد المنفذ من config.py

# تهيئة السجل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    logging.info("جارٍ بدء خدمة البوت...")

    # بدء عميل Telegram
    try:
        await client.start()
        logging.info("تم بدء عميل Telegram بنجاح!")
    except Exception as e:
        logging.error(f"فشل في بدء عميل Telegram: {e}")
        return

    # إنشاء المهام للتعامل مع البوتات
    task1 = asyncio.create_task(
        handle_bot("Bitcoin (BTC) Cloud Pool", "Get Coin 🎁", "🎁 Daily Bonus 🎁")
    )
    task2 = asyncio.create_task(
        handle_bot("Daily (USDT) Claim", "🆔 Account Balance", "🔥 Huge Extra Bonus 🔥")
    )

    # تشغيل تطبيق Quart
    await run_app()

    # انتظار انتهاء المهام
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    logging.info("جارٍ تهيئة التطبيق...")
    with client:
        client.loop.run_until_complete(main())