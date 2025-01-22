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
        message_text = message_text.lower().replace("munite", "minute").replace("sec", "second")

        # تعبيرات عادية لالتقاط جميع الصيغ
        patterns = [
            r"your next available bonus is after (\d+)\s*(minute|minutes|second|seconds)\s*(\d+)\s*(second|seconds)?",  # الصيغة 1
            r"wait:\s*(\d+)\s*(hour|hours|minute|minutes|second|seconds)\s*(\d+)\s*(minute|minutes|second|seconds)?\s*(\d+)\s*(second|seconds)?",  # الصيغة 2
            r"please wait (\d+)\s*(minute|minutes|second|seconds)",  # الصيغة 3
            r"you can claim your bonus again in (\d+)\s*(hour|hours|minute|minutes|second|seconds)[,\s]*(\d+)\s*(minute|minutes|second|seconds)?[,\s]*and\s*(\d+)\s*(second|seconds)?",  # الصيغة 4
        ]

        # البحث عن التطابق الأول
        wait_match = None
        for pattern in patterns:
            wait_match = re.search(pattern, message_text)
            if wait_match:
                break

        if not wait_match:
            logging.warning("لم يتم العثور على وقت انتظار محدد في الرسالة. استخدام القيمة الافتراضية.")
            return int(default_wait)

        # استخراج الأرقام والوحدات
        if wait_match.lastindex >= 5:  # الصيغة 2 أو 4
            hours = int(wait_match.group(1)) if "hour" in wait_match.group(2) else 0
            minutes = int(wait_match.group(3)) if wait_match.group(4) and "minute" in wait_match.group(4) else 0
            seconds = int(wait_match.group(5)) if wait_match.group(6) and "second" in wait_match.group(6) else 0
        elif wait_match.lastindex >= 3:  # الصيغة 1
            minutes = int(wait_match.group(1)) if "minute" in wait_match.group(2) else 0
            seconds = int(wait_match.group(3)) if wait_match.group(4) and "second" in wait_match.group(4) else 0
            hours = 0
        else:  # الصيغة 3
            minutes = int(wait_match.group(1)) if "minute" in wait_match.group(2) else 0
            seconds = int(wait_match.group(1)) if "second" in wait_match.group(2) else 0
            hours = 0

        # حساب وقت الانتظار الكلي بالثواني
        wait_time = hours * 3600 + minutes * 60 + seconds

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