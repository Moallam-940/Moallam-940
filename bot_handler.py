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

        # البحث عن الأرقام المرتبطة بالكلمات الرئيسية
        hours_match = re.search(r"(\d+)\s*(hour|hours)", message_text)
        minutes_match = re.search(r"(\d+)\s*(minute|minutes)", message_text)
        seconds_match = re.search(r"(\d+)\s*(second|seconds)", message_text)

        # استخراج الأرقام
        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(minutes_match.group(1)) if minutes_match else 0
        seconds = int(seconds_match.group(1)) if seconds_match else 0

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
    
    while True:  # إضافة حلقة لتكرار العملية
        try:
            # إرسال الرسالة
            await client.send_message(bot_username, message)
            await asyncio.sleep(10)  # الانتظار 10 ثوانٍ

            # الحصول على آخر رسالة
            messages = await client.get_messages(bot_username, limit=1)
            if not messages:
                logging.error(f"لم يتم العثور على رسائل في البوت {bot_username}.")
                await asyncio.sleep(60)  # الانتظار قبل إعادة المحاولة
                continue  # الانتقال إلى التكرار التالي من الحلقة

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
                                    logging.error(f"حدث خطأ أثناء النقر على الزر: {e}")
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
                logging.error(f"لم يتم العثور على رسائل في البوت {bot_username} بعد الانتظار.")
                await asyncio.sleep(60)  # الانتظار قبل إعادة المحاولة
                continue  # الانتقال إلى التكرار التالي من الحلقة

            last_message = messages[0]

            # استخراج وقت الانتظار من الرسالة باستخدام الدالة المحدثة
            wait_time = await extract_wait_time(last_message.text, default_wait)

            # سجل العملية
            logging.info(f"تقرير البوت {bot_url}: المهلة المعينة = {wait_time} ثانية.")
            await asyncio.sleep(wait_time)  # انتظار المهلة المحددة

        except Exception as e:
            logging.error(f"حدث خطأ في التعامل مع البوت {bot_url}: {e}")
            await asyncio.sleep(60)  # انتظار 60 ثانية قبل إعادة المحاولة في حالة حدوث خطأ