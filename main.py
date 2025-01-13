import asyncio
import logging
from bot_handler import handle_bot, print_report  # استيراد دالة handle_bot و print_report من bot_handler.py
from app import run_app  # استيراد دالة run_app من app.py

# تهيئة السجل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def run_bot(bot_url, message, button_text):
    """
    دالة لتشغيل البوت في حلقة مستقلة.
    """
    while True:
        try:
            await handle_bot(bot_url, message, button_text)
        except Exception as e:
            logging.error(f"حدث خطأ في تشغيل البوت {bot_url}: {e}")
            await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة المحاولة

async def main():
    logging.info("جارٍ بدء خدمة البوت...")

    # روابط البوتات بدلاً من أسماء المستخدمين
    bots = [
        ("https://t.me/DailyUSDTClaimBot", "🆔 Account Balance", "🔥 Huge Extra Bonus 🔥"),
        ("https://t.me/BitcoinBTCCloudPoolBot", "Get Coin 🎁", "🎁 Daily Bonus 🎁"),
        ("https://t.me/DOGSMININGPROBOT", "FREE BONUS 🐶", "⌚ Hourly Bonus"),
        ("https://t.me/USDTMintMasterProV2Bot", "⥴ Extra Bonus", "⌚ Hourly Bonus"),
        ("https://t.me/SOLMineProbot", "❇️ Hourly Bonus", "⌚ Hourly Bonus"),
        ("https://t.me/FreeRipplexrpvipBot", "💸 FREE XRP 💸", "0"),
        ("https://t.me/FreeTetherV3Bot", "🎁 FREE USDT 🎁", "0"),
        ("https://t.me/SolanaInviteBot", "🔥 FREE BONUS", "0"),
        ("https://t.me/TronMinerHubProbot", "⇢ Claim Bonus", "0"),
        ("https://t.me/SOLMinedProbot", "❇️ Hourly Bonus", "0"),
    ]

    # تشغيل كل بوت في مهمة منفصلة
    for bot in bots:
        asyncio.create_task(run_bot(*bot))

    # تشغيل تطبيق Quart
    await run_app()

    # طباعة التقرير بعد الانتهاء من جميع العمليات
    await print_report()

if __name__ == "__main__":
    logging.info("جارٍ تهيئة التطبيق...")
    asyncio.run(main())
