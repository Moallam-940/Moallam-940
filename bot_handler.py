import logging
import asyncio
from telethon import functions
from telethon.tl.types import KeyboardButtonCallback
from telegram_client import client  # تأكد من استيراد العميل الخاص بك (Client)

async def extract_wait_time(message_text, default_wait):
    """
    دالة لاستخراج وقت الانتظار من نص الرسالة بطريقة مختلفة.
    """
    try:
        # تحويل النص إلى حروف صغيرة لتسهيل البحث
        message_text = message_text.lower()

        # تهيئة المتغيرات
        hours = 0
        minutes = 0
        seconds = 0

        # تقسيم النص إلى كلمات
        words = message_text.split()

        # البحث عن الساعات
        if "hour" in words or "hours" in words:
            index = words.index("hour") if "hour" in words else words.index("hours")
            if index > 0 and words[index - 1].isdigit():
                hours = int(words[index - 1])

        # البحث عن الدقائق
        if "minute" in words or "minutes" in words:
            index = words.index("minute") if "minute" in words else words.index("minutes")
            if index > 0 and words[index - 1].isdigit():
                minutes = int(words[index - 1])

        # البحث عن الثواني
        if "second" in words or "seconds" in words:
            index = words.index("second") if "second" in words else words.index("seconds")
            if index > 0 and words[index - 1].isdigit():
                seconds = int(words[index - 1])

        # حساب وقت الانتظار الكلي بالثواني
        wait_time = hours * 3600 + minutes * 60 + seconds

        # إذا لم يتم العثور على أي وقت، نستخدم القيمة الافتراضية
        if wait_time == 0:
            return int(default_wait)

        return wait_time

    except Exception as e:
        logging.error(f"حدث خطأ أثناء استخراج وقت الانتظار: {e}")
        return int(default_wait)

async def handle_bot(bot_url, message, button_text, default_wait):
    """
    دالة غير تزامنية للتعامل مع البوت عبر الرابط.
    """
    bot_username = bot_url.split("/")[-1]  # استخراج اسم البوت من الرابط
    try:
        # إرسال الرسالة
        await client.send_message(bot_username, message)
        await asyncio.sleep(10)  # الانتظار 10 ثوانٍ

        # الحصول على آخر رسالة
        messages = await client.get_messages(bot_username, limit=1)
        if not messages:
            raise Exception(f"لم يتم العثور على رسائل في البوت {bot_username}.")

        last_message = messages[0]

        # البحث عن الزر
        button_clicked = False
        if button_text != "0" and last_message.reply_markup:
            for row in last_message.reply_markup.rows:
                for button in row.buttons:
                    if button_text in button.text:
                        if isinstance(button, KeyboardButtonCallback):
                            try:
                                await client(functions.messages.GetBotCallbackAnswerRequest(
                                    peer=bot_username,
                                    msg_id=last_message.id,
                                    data=button.data
                                ))
                                logging.info(f"تم النقر على الزر '{button.text}' في البوت {bot_url}.")
                            except Exception as e:
                                pass
                        button_clicked = True
                        break
                if button_clicked:
                    break

        # انتظار 10 ثوانٍ بعد النقر على الزر
        if button_clicked:
            await asyncio.sleep(10)

        # الحصول على آخر رسالة مرة أخرى بعد 10 ثوانٍ
        messages = await client.get_messages(bot_username, limit=1)
        if not messages:
            raise Exception(f"لم يتم العثور على رسائل في البوت {bot_username} بعد الانتظار.")

        last_message = messages[0]

        # استخراج وقت الانتظار من الرسالة باستخدام الدالة المحدثة
        wait_time = await extract_wait_time(last_message.text, default_wait)

        # سجل العملية
        logging.info(f"تقرير البوت {bot_url}: المهلة المعينة = {wait_time} ثانية.")
        await asyncio.sleep(wait_time)

    except Exception as e:
        logging.error(f"حدث خطأ في التعامل مع البوت {bot_url}: {e}")