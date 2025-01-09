import os
import re
import asyncio
import logging
from telethon import TelegramClient, functions
from telethon.tl.types import User, KeyboardButtonCallback
from telethon.sessions import StringSession

# إعداد التسجيل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# قراءة المتغيرات البيئية
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
session_string = os.getenv('SESSION_STRING')

# إنشاء العميل باستخدام StringSession
client = TelegramClient(StringSession(session_string), api_id, api_hash)

# مهمة الخلفية (Background Worker) لإبقاء الخدمة نشطة
async def keep_alive():
    while True:
        logging.info("Service is active...")
        await asyncio.sleep(150)  # انتظر 2.5 دقيقة قبل التكرار
        
# دالة لإعادة المحاولة مع حد أقصى
async def retry_operation(operation, max_retries=3, delay=10):
    retry_count = 0
    while retry_count < max_retries:
        try:
            await operation()
            return True  # نجحت العملية
        except Exception as e:
            logging.error(f"Attempt {retry_count + 1} failed: {e}")
            retry_count += 1
            if retry_count < max_retries:
                await asyncio.sleep(delay)  # تأخير قبل إعادة المحاولة
    return False  # فشلت جميع المحاولات

# دالة مشتركة للتعامل مع البوتات
async def handle_bot(target_bot_name, message, button_text):
    while True:  # حلقة لا نهائية لإعادة تشغيل الكود بالكامل
        # البحث عن البوت بالاسم المحدد (مرة واحدة فقط)
        dialogs = await client.get_dialogs()
        target_bot = None
        for dialog in dialogs:
            if isinstance(dialog.entity, User) and dialog.entity.bot and dialog.name == target_bot_name:
                target_bot = dialog.entity
                break

        if not target_bot:
            logging.error(f"Bot with name '{target_bot_name}' not found.")
            await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة التشغيل
            continue

        logging.info(f"Found bot: {target_bot.username}")

        # إرسال رسالة إلى البوت
        send_message_success = await retry_operation(
            lambda: client.send_message(target_bot.username, message),
            max_retries=3,
            delay=10
        )
        if not send_message_success:
            logging.error("Failed to send message after 3 attempts. Restarting in 1 hour...")
            await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة التشغيل
            continue

        logging.info(f"Message '{message}' sent to {target_bot.username}!")

        # الانتظار لرد البوت (مهلة 10 ثواني)
        await asyncio.sleep(10)

        # جلب آخر رسالة في المحادثة
        get_messages_success = await retry_operation(
            lambda: client.get_messages(target_bot.username, limit=1),
            max_retries=3,
            delay=10
        )
        if not get_messages_success:
            logging.error("Failed to get messages after 3 attempts. Restarting in 1 hour...")
            await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة التشغيل
            continue

        messages = await client.get_messages(target_bot.username, limit=1)
        if not messages:
            logging.warning("No messages found in the chat.")
            await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة التشغيل
            continue

        last_message = messages[0]

        # التحقق من وجود أزرار في الرسالة
        if last_message.reply_markup:
            for row in last_message.reply_markup.rows:
                for button in row.buttons:
                    if button_text in button.text:
                        logging.info(f"Found the button: {button_text}")
                        if isinstance(button, KeyboardButtonCallback):
                            click_button_success = await retry_operation(
                                lambda: client(functions.messages.GetBotCallbackAnswerRequest(
                                    peer=target_bot.username,
                                    msg_id=last_message.id,
                                    data=button.data
                                )),
                                max_retries=3,
                                delay=10
                            )
                            if not click_button_success:
                                logging.error("Failed to click button after 3 attempts. Restarting in 1 hour...")
                                await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة التشغيل
                                continue

                            logging.info(f"Button '{button.text}' clicked!")

                            await asyncio.sleep(10)

                            new_messages = await client.get_messages(target_bot.username, limit=1)
                            if new_messages and new_messages[0].id != last_message.id:
                                logging.info("Bot responded with a new message.")
                                logging.info(f"Bot's response: {new_messages[0].text}")

                                # التحقق من وجود العبارة "next available bonus"
                                if "next available bonus" not in new_messages[0].text:
                                    logging.warning("'next available bonus' not found in the message. Retrying...")
                                    await asyncio.sleep(10)  # تأخير قصير قبل إعادة المحاولة
                                    continue  # إعادة المحاولة فقط في هذه الحالة
                                else:
                                    time_match = re.search(r"(\d+)\s*Minute\s*(\d+)\s*Second", new_messages[0].text)
                                    if time_match:
                                        minutes = int(time_match.group(1))
                                        seconds = int(time_match.group(2))
                                        total_seconds = minutes * 60 + seconds + 120  # إضافة دقيقتين (120 ثانية)
                                        logging.info(f"Waiting for {total_seconds} seconds before restarting...")
                                        await asyncio.sleep(total_seconds)
                                    else:
                                        logging.warning("Could not extract time from the message.")
                                        await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة التشغيل
                                        continue
                            else:
                                logging.warning("Bot did not respond with a new message.")
                                await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة التشغيل
                                continue
                        else:
                            logging.warning("Button is not clickable.")
                            await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة التشغيل
                            continue
                    else:
                        logging.warning(f"Button '{button_text}' not found in the last message.")
                        await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة التشغيل
                        continue
        else:
            logging.warning("No buttons found in the last message.")
            await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة التشغيل
            continue

# الدالة الرئيسية
async def main():
    await client.start()

    # تشغيل كل بوت كمهمة منفصلة
    task1 = asyncio.create_task(
        handle_bot("Bitcoin (BTC) Cloud Pool", "Get Coin 🎁", "🎁 Daily Bonus 🎁")
    )
    task2 = asyncio.create_task(
        handle_bot("Daily (USDT) Claim", "🆔 Account Balance", "🔥 Huge Extra Bonus 🔥")
    )

    # الانتظار حتى انتهاء المهام (لن يحدث هذا أبدًا لأن المهام تعمل بشكل مستمر)
    await asyncio.gather(task1, task2)

# تشغيل البرنامج
if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
