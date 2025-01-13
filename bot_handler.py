import logging
import asyncio
import re
from telethon import functions
from telegram_client import client

# تهيئة السجل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def handle_bot(target_bot_name, message, button_text, default_wait_duration):
    """
    دالة غير تزامنية (async) للتعامل مع البوت.
    """
    logging.info(f"جارٍ بدء التعامل مع البوت '{target_bot_name}'...")
    
    try:
        # التحقق من أن العميل متصل
        if not client.is_connected():
            logging.info("جارٍ توصيل العميل...")
            await client.connect()

        # التحقق من أن العميل مصرح له بالاتصال
        if not await client.is_user_authorized():
            logging.error("العميل غير مصرح له. يرجى التحقق من جلسة العمل.")
            await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة المحاولة
            return

        # الوصول إلى البوت مباشرة باستخدام المعرف
        target_bot = await client.get_entity(target_bot_name)
        logging.info(f"تم العثور على البوت: {target_bot.username}")

        # إرسال الرسالة إلى البوت
        logging.info(f"جارٍ إرسال الرسالة '{message}' إلى {target_bot.username}...")
        await client.send_message(target_bot, message)
        logging.info(f"تم إرسال الرسالة '{message}' إلى {target_bot.username}!")

        # الانتظار لمدة 10 ثواني
        await asyncio.sleep(10)

        # محاولة الحصول على آخر رسالة من البوت
        try:
            messages = await client.get_messages(target_bot.username, limit=1)
            if not messages:
                logging.warning("لم يتم العثور على رسائل في الدردشة.")
                raise Exception("لم يتم العثور على رسائل في الدردشة.")
        except Exception as e:
            logging.error(f"فشل في الحصول على الرسائل: {e}")
            return

        last_message = messages[0]
        logging.info(f"آخر رسالة من البوت: {last_message.text}")

        # تجاهل عمليات البحث عن الزر أو النقر عليه في حالة وجوده أو عدمه

        # محاولة استخراج الوقت من الرسالة
        try:
            time_match = re.search(
                r"(\d+)\s*hours?,\s*(\d+)\s*minutes?,\s*and\s*(\d+)\s*seconds?",
                last_message.text,
                re.IGNORECASE
            )
            if time_match:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                seconds = int(time_match.group(3))
                total_seconds = (hours * 3600) + (minutes * 60) + seconds
                logging.info(f"جارٍ الانتظار لمدة {total_seconds} ثانية ({hours} ساعات، {minutes} دقائق، {seconds} ثواني) قبل إعادة التشغيل...")
                await asyncio.sleep(total_seconds)
            else:
                logging.info(f"لم يتم العثور على وقت في الرسالة. سيتم استخدام المهلة الافتراضية: {default_wait_duration} ثانية.")
                await asyncio.sleep(default_wait_duration)
        except Exception as e:
            logging.error(f"حدث خطأ أثناء استخراج الوقت: {e}")
            logging.info(f"سيتم استخدام المهلة الافتراضية: {default_wait_duration} ثانية.")
            await asyncio.sleep(default_wait_duration)

        # تقرير العملية
        report = {
            "bot_username": target_bot.username,
            "wait_duration": default_wait_duration
        }

        logging.info(f"تقرير العملية:\n"
                     f"- اسم البوت: {report['bot_username']}\n"
                     f"- مدة الانتظار: {report['wait_duration']} ثانية.")

    except Exception as e:
        logging.error(f"حدث خطأ أثناء التعامل مع البوت: {e}")
