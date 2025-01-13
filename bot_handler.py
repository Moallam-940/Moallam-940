import logging
import asyncio
import re
from telethon import functions
from telethon.tl.types import KeyboardButtonCallback
from telegram_client import client  # تأكد من استيراد العميل الخاص بك (Client)

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
                                #logging.warning(f"فشل في النقر على الزر: {e}. سيتم تجاهل الخطأ والمتابعة.")
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

# استخراج وقت الانتظار من الرسالة
wait_time = None
last_message_text = "🕐 You can claim your bonus again in 16 hours, 29 minutes, and 26 seconds."

if last_message.text:
    # تعديل التعبير العادي ليشمل الساعات، الدقائق، والثواني مع المسافات والفواصل
    match = re.search(r"(?:(\d+)\s*(?:hour|hours?)\s*,?\s*)?(?:(\d+)\s*(?:minute|minutes?)\s*,?\s*)?(\d+)\s*(?:second|seconds?)", last_message_text, re.IGNORECASE)
    if match:
        hours = int(match.group(1) or 0)  # تعيين الساعات إلى صفر إذا لم توجد
        minutes = int(match.group(2) or 0)  # تعيين الدقائق إلى صفر إذا لم توجد
        seconds = int(match.group(3) or 0)  # تعيين الثواني إلى صفر إذا لم توجد
        wait_time = hours * 3600 + minutes * 60 + seconds

        # تعيين المهلة الافتراضية إذا لم يتم العثور على وقت
        if wait_time is None:
            wait_time = int(default_wait)

        # سجل العملية
        logging.info(f"تقرير البوت {bot_url}: المهلة المعينة = {wait_time} ثانية.")
        await asyncio.sleep(wait_time)

    except Exception as e:
        # هنا يمكن إلغاء تسجيل الأخطاء
        pass  # ببساطة لا نفعل شيئاً إذا حدث خطأ