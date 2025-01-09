import asyncio
import logging
from telegram_client import client
from bot_handler import handle_bot
from app import run_app

# إعدادات التسجيل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    """
    الدالة الرئيسية لتشغيل التطبيق.
    """
    logging.info("Starting the bot service...")
    await client.start()  # بدء عميل Telegram

    # إنشاء مهام للتعامل مع البوتات
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
    logging.info("Initializing the application...")
    with client:
        client.loop.run_until_complete(main())