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
    # التعبير العادي المحدث
    pattern = re.compile(
        r"(\d+)\s*(?:hour|hours?)\s*,?\s*(\d+)\s*(?:minute|minutes?)\s*,?\s*(\d+)\s*(?:second|seconds?)|"
        r"(\d+)\s*(?:minute|minutes?)\s*(\d+)\s*(?:sec|seconds?)|"
        r"(\d+)\s*(?:hour|hours?)\s*(\d+)\s*(?:minute|minutes?)|"
        r"(\d+)\s*(?:minute|minutes?)|"
        r"(\d+)\s*(?:second|seconds?)",
        re.IGNORECASE
    )

    match = pattern.search(message_text)
    if match:
        # استخراج الأرقام من التطابق
        hours = int(match.group(1) or 0) if match.group(1) else 0
        minutes = int(match.group(2) or 0) if match.group(2) else 0
        seconds = int(match.group(3) or 0) if match.group(3) else 0

        # إذا كان النموذج يحتوي على دقائق وثواني فقط
        if match.group(4) and match.group(5):
            minutes = int(match.group(4))
            seconds = int(match.group(5))

        # إذا كان النموذج يحتوي على ساعات ودقائق فقط
        elif match.group(6) and match.group(7):
            hours = int(match.group(6))
            minutes = int(match.group(7))

        # إذا كان النموذج يحتوي على دقائق فقط
        elif match.group(8):
            minutes = int(match.group(8))

        # إذا كان النموذج يحتوي على ثواني فقط
        elif match.group(9):
            seconds = int(match.group(9))

        # حساب وقت الانتظار الكلي بالثواني
        wait_time = hours * 3600 + minutes * 60 + seconds
        return wait_time

    # إذا لم يتم العثور على تطابق، يتم استخدام المهلة الافتراضية
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