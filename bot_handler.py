import logging
import asyncio
import re
from telethon import functions
from telethon.tl.types import KeyboardButtonCallback
from telegram_client import client  # تأكد من استيراد العميل الخاص بك (Client)

async def extract_wait_time(message_text, default_wait):
    """
    دالة لاستخراج وقت الانتظار من نص الرسالة.
    """
    try:
        # تحويل النص إلى حروف صغيرة وتصحيح الأخطاء الإملائية
        message_text = message_text.lower().replace("munite", "minute")

        # استخدام تعبير عادي أكثر مرونة
        time_matches = re.findall(r"(\d+)\s*(hour|hours|minute|minutes|second|seconds)", message_text)

        if not time_matches:
            logging.warning("لم يتم العثور على وقت انتظار في الرسالة. استخدام القيمة الافتراضية.")
            return int(default_wait)

        # حساب وقت الانتظار الكلي بالثواني
        wait_time = 0
        for value, unit in time_matches:
            value = int(value)
            if "hour" in unit:
                wait_time += value * 3600
            elif "minute" in unit:
                wait_time += value * 60
            elif "second" in unit:
                wait_time += value

        # إضافة 60 ثانية كهامش أمان
        return wait_time + 60

    except Exception as e:
        logging.error(f"حدث خطأ أثناء استخراج وقت الانتظار: {e}")
        return int(default_wait)

async def handle_bot(bot_url, message, button_text, default_wait):
    """
    دالة غير تزامنية للتعامل مع البوت عبر الرابط.
    """
    bot_username = bot_url.split("/")[-1]  # استخراج اسم البوت من الرابط
    
    while True:  # حلقة لتكرار العملية
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
                                    logging.error(f"فشل في النقر على الزر: {e}")
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