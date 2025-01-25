import asyncio
import logging
from bot_handler import handle_bot  # استيراد دالة handle_bot من bot_handler.py
from app import run_app  # استيراد دالة run_app من app.py
from telegram_client import client  # استيراد العميل من ملف telegram_client.py

# تهيئة السجل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def ensure_client_connection():
    """
    دالة للتأكد من أن العميل متصل ومصرح له.
    """
    if not client.is_connected():
        await client.connect()
    if not await client.is_user_authorized():
        logging.error("الجلسة غير مصرح بها. يرجى تسجيل الدخول.")
        return False
    return True

async def main():
    logging.info("جارٍ بدء خدمة البوت...")

    # التحقق من اتصال العميل
    if not await ensure_client_connection():
        return

    # (رابط البوت، الرسالة المطلوب ارسالها، النص المطلوب البحث عنه في الزر، المهلة الافتراضية، النص المطلوب استخراج المهلة منه)
    bots = [
        
        ("https://t.me/BitcoinBTCCloudPoolBot", "Get Coin 🎁", "🎁 Daily Bonus 🎁", "3600", "Your next available bonus is after"),
        ("https://t.me/DOGSMININGPROBOT", "FREE BONUS 🐶", "⌚ Hourly Bonus", "3600", "Your next available bonus is after"),
        ("https://t.me/USDTMintMasterProV2Bot", "⥴ Extra Bonus", "⌚ Hourly Bonus", "3600", "Your next available bonus is after"),
        ("https://t.me/SOLMineProbot", "❇️ Hourly Bonus", "⌚ Hourly Bonus", "3600", "Your next available bonus is after"),
        ("https://t.me/FreeRipplexrpvipBot", "💸 FREE XRP 💸", "0", "86400", "You can claim your bonus again in"),
        ("https://t.me/FreeTetherV3Bot", "🎁 FREE USDT 🎁", "0", "86400", "You can claim your bonus again in"),
        ("https://t.me/SolanaInviteBot", "🔥 FREE BONUS", "0", "86400", "You can claim your bonus again in"),
        ("https://t.me/TronMinerHubProbot", "⇢ Claim Bonus", "0", "3600", "Your next available bonus is after"),
        ("https://t.me/SOLMinedProbot", "❇️ Hourly Bonus", "0", "3600", "Your next available bonus is after"),
("https://t.me/BNBMiningMaestrov2bot", "🎁 HORLY BONUS", "0", "3600", "Your next available bonus is after"),
("https://t.me/USDTMintMasterProBot", "⥴ Extra Bonus", "0", "3600", "Your next available bonus is after"),
("https://t.me/TetherTreasureMinerBot", "⇢ Bonus Rewards", "0", "3600", "Your next available bonus is after"),
("https://t.me/TrxPayProv2bot", "🔺🔻 FREE TRX 🔺🔻", "0", "3600", "Please wait"),
("https://t.me/get_free_bitcoin_now_bot", "🎁 Bonus", "Receive", "28800", "Wait:"),
]

    # تشغيل كل بوت في مهمة منفصلة
    for bot in bots:
        asyncio.create_task(handle_bot(*bot))

    # تشغيل تطبيق Quart
    await run_app()

if __name__ == "__main__":
    logging.info("جارٍ تهيئة التطبيق...")
    asyncio.run(main())