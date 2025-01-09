import asyncio
import logging
import os
from telegram_client import client  # استيراد العميل من telegram_client.py
from bot_handler import handle_bot
from app import run_app
from config import port  # استيراد المنفذ من config.py

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    logging.info("Starting the bot service...")

    # بدء عميل Telegram
    try:
        await client.start()
        logging.info("Telegram client started successfully!")
    except Exception as e:
        logging.error(f"Failed to start Telegram client: {e}")
        return

    # طباعة معلومات الجلسة والمتغيرات البيئية
    logging.info(f"API_ID: {os.getenv('API_ID')}, API_HASH: {os.getenv('API_HASH')}, SESSION_STRING: {os.getenv('SESSION_STRING')}")

    # إنشاء المهام للتعامل مع البوتات
    task1 = asyncio.create_task(
        handle_bot("Bitcoin (BTC) Cloud Pool", "Get Coin 🎁", "🎁 Daily Bonus 🎁")
    )
    task2 = asyncio.create_task(
        handle_bot("Daily (USDT) Claim", "🆔 Account Balance", "🔥 Huge Extra Bonus 🔥")
    )

logging.info("Tasks created successfully!")

    # تشغيل التطبيق
    await run_app()

    # انتظار انتهاء المهام
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    logging.info("Initializing the application...")
    with client:
        client.loop.run_until_complete(main())