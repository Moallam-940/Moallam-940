import asyncio
import logging
import re
from telethon import functions
from telethon.tl.types import User, KeyboardButtonCallback
from telegram_client import client

# إعدادات التسجيل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def handle_bot(target_bot_name, message, button_text):
    """
    دالة للتعامل مع البوتات على Telegram.
    
    :param target_bot_name: اسم البوت المستهدف.
    :param message: الرسالة المرسلة إلى البوت.
    :param button_text: النص الموجود على الزر الذي نريد النقر عليه.
    """
    while True:
        # التحقق من أن العميل مصرح له بالاتصال
        if not await client.is_user_authorized():
            logging.error("Client is not authorized. Please check the session string.")
            await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة المحاولة
            continue

        # الحصول على الدردشات (المحادثات) المتاحة
        dialogs = await client.get_dialogs()
        target_bot = None

        # البحث عن البوت المستهدف في الدردشات
        for dialog in dialogs:
            if isinstance(dialog.entity, User) and dialog.entity.bot and dialog.name == target_bot_name:
                target_bot = dialog.entity
                break
            elif isinstance(dialog.entity, User) and dialog.entity.bot:
                logging.info(f"Found bot: {dialog.name} (Username: {dialog.entity.username})")

        # إذا لم يتم العثور على البوت
        if not target_bot:
            logging.error(f"Bot with name '{target_bot_name}' not found.")
            await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة المحاولة
            continue

        logging.info(f"Found bot: {target_bot.username}")

        # محاولة إرسال رسالة إلى البوت
        try:
            await client.send_message(target_bot.username, message)
            logging.info(f"Message '{message}' sent to {target_bot.username}!")
        except Exception as e:
            logging.error(f"Failed to send message to {target_bot.username}: {e}")
            await asyncio.sleep(10)  # الانتظار لمدة 10 ثواني قبل إعادة المحاولة
            continue

        await asyncio.sleep(10)  # الانتظار لمدة 10 ثواني

        # الحصول على آخر رسالة من البوت
        messages = await client.get_messages(target_bot.username, limit=1)
        if not messages:
            logging.warning("No messages found in the chat.")
            await asyncio.sleep(10)  # الانتظار لمدة 10 ثواني قبل إعادة المحاولة
            continue

        last_message = messages[0]
        logging.info(f"Last message from bot: {last_message.text}")

        # التحقق من وجود أزرار في الرسالة
        if last_message.reply_markup:
            for row in last_message.reply_markup.rows:
                for button in row.buttons:
                    if button_text in button.text:
                        logging.info(f"Found the button: {button_text}")
                        if isinstance(button, KeyboardButtonCallback):
                            try:
                                # النقر على الزر باستخدام بيانات الزر
                                await client(functions.messages.GetBotCallbackAnswerRequest(
                                    peer=target_bot.username,
                                    msg_id=last_message.id,
                                    data=button.data
                                ))
                                logging.info(f"Button '{button.text}' clicked!")
                            except Exception as e:
                                logging.error(f"Failed to receive response after clicking button: {e}")
                                pass

                            await asyncio.sleep(10)  # الانتظار لمدة 10 ثواني

                            # الحصول على الرسائل الجديدة بعد النقر على الزر
                            new_messages = await client.get_messages(target_bot.username, limit=1)
                            if new_messages and new_messages[0].id != last_message.id:
                                logging.info("Bot responded with a new message.")
                                logging.info(f"Bot's response: {new_messages[0].text}")

                                # التحقق من وجود نص معين في الرسالة الجديدة
                                if "next available bonus" not in new_messages[0].text:
                                    logging.warning("'next available bonus' not found in the message. Retrying...")
                                    await asyncio.sleep(10)  # الانتظار لمدة 10 ثواني قبل إعادة المحاولة
                                    continue
                                else:
                                    # استخراج الوقت من الرسالة
                                    time_match = re.search(r"(\d+)\s*Minute\s*(\d+)\s*Second", new_messages[0].text)
                                    if time_match:
                                        minutes = int(time_match.group(1))
                                        seconds = int(time_match.group(2))
                                        total_seconds = minutes * 60 + seconds + 120
                                        logging.info(f"Waiting for {total_seconds} seconds before restarting...")
                                        await asyncio.sleep(total_seconds)  # الانتظار للوقت المحدد
                                    else:
                                        logging.warning("Could not extract time from the message.")
                                        await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة المحاولة
                                        continue
                            else:
                                logging.warning("Bot did not respond with a new message.")
                                pass
                        else:
                            logging.warning("Button is not clickable.")
                            await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة المحاولة
                            continue
                    else:
                        logging.warning(f"Button '{button_text}' not found in the last message.")
                        await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة المحاولة
                        continue
        else:
            logging.warning("No buttons found in the last message.")
            await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة المحاولة
            continue