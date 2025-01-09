import asyncio
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession
from config import api_id, api_hash, session_string

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
    logging.info(f"API_ID: {api_id}, API_HASH: {api_hash}, SESSION_STRING: {session_string}")

    # إنشاء المهام للتعامل مع البوتات
    task1 = asyncio.create_task(
        handle_bot("Bitcoin (BTC) Cloud Pool", "Get Coin 🎁", "🎁 Daily Bonus 🎁")
    )
    task2 = asyncio.create_task(
        handle_bot("Daily (USDT) Claim", "🆔 Account Balance", "🔥 Huge Extra Bonus 🔥")
    )

    # تشغيل التطبيق
    port = int(os.getenv('PORT', 8080))
    await app.run_task(host='0.0.0.0', port=port)

    # انتظار انتهاء المهام
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    logging.info("Initializing the application...")
    with client:
        client.loop.run_until_complete(main())