import logging
import asyncio
import re
from telethon import functions
from telethon.tl.types import KeyboardButtonCallback
from telegram_client import client  # تأكد من استيراد العميل الخاص بك (Client)

async def extract_wait_time(message_text, default_wait):
    """
    دالة لاستخراج وقت الانتظار من نص الرسالة بطريقة جديدة.
    """
    try:
        # تحويل النص إلى حروف صغيرة لتسهيل البحث
        message_text = message_text.lower()

        # تهيئة المتغيرات
        hours = 0
        minutes = 0
        seconds = 0

        # تقسيم النص إلى أجزاء باستخدام الفواصل والكلمات الرئيسية
        parts = re.split(r"[\s,]+", message_text)

        # البحث عن الأرقام المرتبطة بالكلمات الرئيسية
        for i, part in enumerate(parts):
            if part.isdigit():
                # إذا كان الجزء رقمًا، نتحقق من الجزء التالي
                if i + 1 < len(parts):
                    next_part = parts[i + 1]
                    if "hour" in next_part or "hours" in next_part:
                        hours = int(part)
                    elif "minute" in next_part or "minutes" in next_part:
                        minutes = int(part)
                    elif "second" in next_part or "seconds" in next_part:
                        seconds = int(part)

        # حساب وقت الانتظار الكلي بالثواني
        wait_time = hours * 3600 + minutes * 60 + seconds + 60

        # إذا لم يتم العثور على أي وقت، نستخدم القيمة الافتراضية
        if wait_time == 0:
            return int(default_wait + 60)

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