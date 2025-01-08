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
api_id = os.getenv('API_ID')  # API_ID من متغيرات البيئة
api_hash = os.getenv('API_HASH')  # API_HASH من متغيرات البيئة
session_string = os.getenv('SESSION_STRING')  # SESSION_STRING من متغيرات البيئة

# التحقق من وجود المتغيرات البيئية
if not api_id or not api_hash or not session_string:
    logging.error("يجب تعيين API_ID و API_HASH و SESSION_STRING في متغيرات البيئة.")
    exit(1)

# إنشاء العميل باستخدام StringSession
client = TelegramClient(StringSession(session_string), api_id, api_hash)

# دالة مشتركة للتعامل مع البوتات
async def handle_bot(target_bot_name, message, button_text):
    # البحث عن البوت بالاسم المحدد (مرة واحدة فقط)
    dialogs = await client.get_dialogs()
    target_bot = None
    for dialog in dialogs:
        if isinstance(dialog.entity, User) and dialog.entity.bot and dialog.name == target_bot_name:
            target_bot = dialog.entity
            break

    if not target_bot:
        logging.error(f"Bot with name '{target_bot_name}' not found.")
        return

    logging.info(f"Found bot: {target_bot.username}")

    while True:  # تكرار العملية لكل بوت
        # إرسال رسالة إلى البوت
        try:
            await client.send_message(target_bot.username, message)
            logging.info(f"Message '{message}' sent to {target_bot.username}!")
        except Exception as e:
            logging.error(f"Failed to send message to {target_bot.username}: {e}")
           # await asyncio.sleep(10)  # تأخير قصير قبل إعادة المحاولة
           # continue

        # الانتظار لرد البوت (مهلة 10 ثواني)
        await asyncio.sleep(10)

        # جلب آخر رسالة في المحادثة
        messages = await client.get_messages(target_bot.username, limit=1)
        if not messages:
            logging.warning("No messages found in the chat.")
           # await asyncio.sleep(10)  # تأخير قصير قبل إعادة المحاولة
           # continue

        last_message = messages[0]

        # التحقق من وجود أزرار في الرسالة
        if last_message.reply_markup:
            for row in last_message.reply_markup.rows:
                for button in row.buttons:
                    if button_text in button.text:
                        logging.info(f"Found the button: {button_text}")
                        if isinstance(button, KeyboardButtonCallback):
                            try:
                                await client(functions.messages.GetBotCallbackAnswerRequest(
                                    peer=target_bot.username,
                                    msg_id=last_message.id,
                                    data=button.data
                                ))
                                logging.info(f"Button '{button.text}' clicked!")
                            except Exception as e:
                                logging.error(f"Button clicked, but bot did not respond: {e}")
                               # await asyncio.sleep(10)  # تأخير قصير قبل إعادة المحاولة
                               # continue

                            await asyncio.sleep(10)

                            new_messages = await client.get_messages(target_bot.username, limit=1)
                            if new_messages and new_messages[0].id != last_message.id:
                                logging.info("Bot responded with a new message.")
                                logging.info(f"Bot's response: {new_messages[0].text}")

                                if "next available bonus" in new_messages[0].text:
                                    time_match = re.search(r"(\d+)\s*Minute\s*(\d+)\s*Second", new_messages[0].text)
                                    if time_match:
                                        minutes = int(time_match.group(1))
                                        seconds = int(time_match.group(2))
                                        total_seconds = minutes * 60 + seconds + 120  # إضافة دقيقتين (120 ثانية)
                                        logging.info(f"Waiting for {total_seconds} seconds before restarting...")
                                        await asyncio.sleep(total_seconds)
                                    else:
                                        logging.warning("Could not extract time from the message.")
                                        await asyncio.sleep(10)  # تأخير قصير قبل إعادة المحاولة
                                        continue
                            else:
                                logging.warning("Bot did not respond with a new message.")
                               # await asyncio.sleep(10)  # تأخير قصير قبل إعادة المحاولة
                               # continue
                        else:
                            logging.warning("Button is not clickable.")
                          #  await asyncio.sleep(10)  # تأخير قصير قبل إعادة المحاولة
                           # continue
                    else:
                        logging.warning(f"Button '{button_text}' not found in the last message.")
                      #  await asyncio.sleep(10)  # تأخير قصير قبل إعادة المحاولة
                      #  continue

        # التحقق من وجود العبارة "next available bonus"
        if "next available bonus" not in last_message.text:
            logging.warning("'next available bonus' not found in the message. Restarting the bot...")
           # await asyncio.sleep(10)  # تأخير قصير قبل إعادة التشغيل
          #  continue  # إعادة التشغيل من البداية

# تشغيل البوتات بشكل مستقل
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

    await client.disconnect()

# تشغيل البرنامج
if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
