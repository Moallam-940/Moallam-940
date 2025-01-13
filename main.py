import asyncio
import logging
from bot_handler import handle_bot  # استيراد دالة handle_bot من bot_handler.py
from app import run_app  # استيراد دالة run_app من app.py

# تهيئة السجل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def run_bot(bot_url, message, button_text, default_wait, report_list):
    """
    دالة لتشغيل البوت وإضافة تقريره إلى القائمة المشتركة.
    """
    report = await handle_bot(bot_url, message, button_text, default_wait)
    report_list.append(report)

async def main():
    logging.info("جارٍ بدء خدمة البوت...")

    # (رابط البوت، الرسالة المطلوب ارسالها، النص المطلوب البحث عنه في الزر، المهلة الافتراضية) 
    bots = [
        ("https://t.me/DailyUSDTClaimBot", "🆔 Account Balance", "🔥 Huge Extra Bonus 🔥", 3600),
        ("https://t.me/BitcoinBTCCloudPoolBot", "Get Coin 🎁", "🎁 Daily Bonus 🎁", 3600),
        ("https://t.me/DOGSMININGPROBOT", "FREE BONUS 🐶", "⌚ Hourly Bonus", 3600),
        ("https://t.me/USDTMintMasterProV2Bot", "⥴ Extra Bonus", "⌚ Hourly Bonus", 3600),
        ("https://t.me/SOLMineProbot", "❇️ Hourly Bonus", "⌚ Hourly Bonus", 3600),
        ("https://t.me/FreeRipplexrpvipBot", "💸 FREE XRP 💸", "0", 86400),
        ("https://t.me/FreeTetherV3Bot", "🎁 FREE USDT 🎁", "0", 86400),
        ("https://t.me/SolanaInviteBot", "🔥 FREE BONUS", "0", 86400),
        ("https://t.me/TronMinerHubProbot", "⇢ Claim Bonus", "0", 3600),
        ("https://t.me/SOLMinedProbot", "❇️ Hourly Bonus", "0", 3600),
    ]

    # قائمة لتجميع التقارير
    reports = []

    # تشغيل كل بوت في مهمة منفصلة وجمع التقارير
    tasks = [run_bot(*bot, reports) for bot in bots]
    await asyncio.gather(*tasks)

    # طباعة التقرير الشامل
    logging.info("تقرير العملية الشامل:")
    for report in reports:
        logging.info(f"- رابط البوت: {report['bot_url']}، المهلة: {report['wait_duration']} ثانية")

    # تشغيل تطبيق Quart
    await run_app()

if __name__ == "__main__":
    logging.info("جارٍ تهيئة التطبيق...")
    asyncio.run(main())
