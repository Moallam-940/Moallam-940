import asyncio
import logging
from bot_handler import handle_bot  # استيراد دالة handle_bot من bot_handler.py
from app import run_app  # استيراد دالة run_app من app.py

# تهيئة السجل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    logging.info("جارٍ بدء خدمة البوت...")

    # إنشاء المهام للتعامل مع البوتات
    task1 = asyncio.create_task(handle_bot("Daily (USDT) Claim", "🆔 Account Balance", "🔥 Huge Extra Bonus 🔥"))
    task2 = asyncio.create_task(handle_bot("Bitcoin (BTC) Cloud Pool", "Get Coin 🎁", "🎁 Daily Bonus 🎁"))
    task3 = asyncio.create_task(handle_bot("DOGS MINING BOT 🦴", "FREE BONUS 🐶", "⌚ Hourly Bonus"))
    task4 = asyncio.create_task(handle_bot("USDŦ Mint Master Pro Bot", "⥴ Extra Bonus", "⌚ Hourly Bonus"))
    task5 = asyncio.create_task(handle_bot("SOLANA MINED PRO BOT 🔵", "❇️ Hourly Bonus", "⌚ Hourly Bonus"))
    task6 = asyncio.create_task(handle_bot("Free Ripple (XRP)", "💸 FREE XRP 💸", "0"))
    task7 = asyncio.create_task(handle_bot("Free Tether USDT 🎁", "🎁 FREE USDT 🎁", "0"))
    task8 = asyncio.create_task(handle_bot("Solana Invite", "🔥 FREE BONUS", "0"))

    # تشغيل تطبيق Quart
    await run_app()

    # انتظار انتهاء المهام
    await asyncio.gather(task1, task2, task3, task4, task5, task6, task7, task8)

if __name__ == "__main__":
    logging.info("جارٍ تهيئة التطبيق...")
    asyncio.run(main())