import asyncio
import logging
from bot_handler import handle_bot  # استيراد دالة handle_bot من bot_handler.py
from app import run_app  # استيراد دالة run_app من app.py

# تهيئة السجل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def run_bot(bot_name, message, button_text):
    """
    دالة لتشغيل البوت في حلقة مستقلة.
    """
    while True:
        try:
            await handle_bot(bot_name, message, button_text)
        except Exception as e:
            logging.error(f"حدث خطأ في تشغيل البوت {bot_name}: {e}")
            await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة المحاولة

async def main():
    logging.info("جارٍ بدء خدمة البوت...")

    # إنشاء المهام للتعامل مع البوتات
    bots = [
        ("@DailyUSDTClaimBot", "🆔 Account Balance", "🔥 Huge Extra Bonus 🔥"),
        ("@BitcoinBTCCloudPoolBot", "Get Coin 🎁", "🎁 Daily Bonus 🎁"),
        ("@DOGSMININGPROBOT", "FREE BONUS 🐶", "⌚ Hourly Bonus"),
        ("@USDTMintMasterProV2Bot", "⥴ Extra Bonus", "⌚ Hourly Bonus"),
        ("@SOLMineProbot", "❇️ Hourly Bonus", "⌚ Hourly Bonus"),
        ("@FreeRipplexrpvipBot", "💸 FREE XRP 💸", "0"),
        ("@FreeTetherV3Bot", "🎁 FREE USDT 🎁", "0"),
        ("@SolanaInviteBot", "🔥 FREE BONUS", "0"),
("@TronMinerHubProbot", "⇢ Claim Bonus", "0"),
("@SOLMinedProbot", "❇️ Hourly Bonus", "0"),
    ]

    # تشغيل كل بوت في مهمة منفصلة
    for bot in bots:
        asyncio.create_task(run_bot(*bot))

    # تشغيل تطبيق Quart
    await run_app()

if __name__ == "__main__":
    logging.info("جارٍ تهيئة التطبيق...")
    asyncio.run(main())