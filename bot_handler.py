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
    try:
        bot_username = bot_url.split("/")[-1]  # استخراج اسم البوت
        await client.send_message(bot_username, message)
        await asyncio.sleep(10)

        messages = await client.get_messages(bot_username, limit=1)
        last_message = messages[0] if messages else None

        wait_duration = default_wait  # القيمة الافتراضية للمهلة
        if last_message:
            # البحث عن الزر في الرسالة الأخيرة
            if button_text != "0" and last_message.reply_markup:
                for row in last_message.reply_markup.rows:
                    for button in row.buttons:
                        if button_text in button.text:
                            if isinstance(button, KeyboardButtonCallback):
                                await client(functions.messages.GetBotCallbackAnswerRequest(
                                    peer=bot_username,
                                    msg_id=last_message.id,
                                    data=button.data
                                ))
                            break

            # محاولة استخراج الوقت من الرسالة
            time_match = re.search(r"(\d+)\s*hours?,\s*(\d+)\s*minutes?,\s*(\d+)\s*seconds?", last_message.text, re.IGNORECASE)
            if time_match:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                seconds = int(time_match.group(3))
                wait_duration = (hours * 3600) + (minutes * 60) + seconds

        # العودة بتقرير البوت
        return {
            "bot_url": bot_url,
            "wait_duration": wait_duration,
        }

    except Exception as e:
        logging.error(f"حدث خطأ مع البوت {bot_url}: {e}")
        return {
            "bot_url": bot_url,
            "wait_duration": default_wait,  # إذا حدث خطأ نعود بالقيمة الافتراضية
        }
