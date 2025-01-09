import asyncio
import logging
import re
from telethon import functions
from telethon.tl.types import User, KeyboardButtonCallback
from telegram_client import client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def handle_bot(target_bot_name, message, button_text):
    """
    دالة للتعامل مع البوتات على Telegram.
    
    :param target_bot_name: اسم البوت المستهدف.
    :param message: الرسالة المرسلة إلى البوت.
    :param button_text: النص الموجود على الزر الذي نريد النقر عليه.
    """
    retry_count = 1  # عدد مرات إعادة التشغيل المسموح بها
    max_retries = 1  # الحد الأقصى لعدد المحاولات

    while True:
        try:
            # التحقق من أن العميل مصرح له بالاتصال
            if not await client.is_user_authorized():
                logging.error("Client is not authorized. Please check the session string.")
                await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة المحاولة
                continue

            # إرسال الرسالة إلى البوت
            logging.info(f"Sending message '{message}' to {target_bot_name}...")
            await client.send_message(target_bot_name, message)
            logging.info(f"Message '{message}' sent to {target_bot_name}!")

            # الانتظار لمدة 10 ثواني
            await asyncio.sleep(10)

            # الحصول على آخر رسالة من البوت
            messages = await client.get_messages(target_bot_name, limit=1)
            if not messages:
                logging.warning("No messages found in the chat.")
                if retry_count >= max_retries:
                    logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                    await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                    retry_count = 0  # إعادة تعيين عدد المحاولات
                retry_count += 1
                continue

            last_message = messages[0]
            logging.info(f"Last message from bot: {last_message.text}")

            # البحث عن الزر المطلوب في الرسالة الأخيرة
            if last_message.reply_markup:
                button_found = False
                for row in last_message.reply_markup.rows:
                    for button in row.buttons:
                        if button_text in button.text:
                            logging.info(f"Found the button: {button_text}")
                            button_found = True

                            # الضغط على الزر
                            if isinstance(button, KeyboardButtonCallback):
                                try:
                                    await client(functions.messages.GetBotCallbackAnswerRequest(
                                        peer=target_bot_name,
                                        msg_id=last_message.id,
                                        data=button.data
                                    ))
                                    logging.info(f"Button '{button.text}' clicked!")
                                except Exception as e:
                                    logging.error(f"Failed to receive response after clicking button: {e}")
                                    if retry_count >= max_retries:
                                        logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                                        await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                                        retry_count = 0  # إعادة تعيين عدد المحاولات
                                    retry_count += 1
                                    continue

                            # الانتظار لمدة 10 ثواني بعد النقر على الزر
                            await asyncio.sleep(10)

                            # الحصول على الرسائل الجديدة بعد النقر على الزر
                            new_messages = await client.get_messages(target_bot_name, limit=1)
                            if new_messages and new_messages[0].id != last_message.id:
                                logging.info("Bot responded with a new message.")
                                logging.info(f"Bot's response: {new_messages[0].text}")

                                # التحقق من وجود العبارة المطلوبة في الرسالة الجديدة
                                if "next available bonus" not in new_messages[0].text:
                                    logging.warning("'next available bonus' not found in the message.")
                                    if retry_count >= max_retries:
                                        logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                                        await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                                        retry_count = 0  # إعادة تعيين عدد المحاولات
                                    retry_count += 1
                                    continue
                                else:
                                    # استخراج الوقت من الرسالة
                                    time_match = re.search(r"(\d+)\s*Minute\s*(\d+)\s*Second", new_messages[0].text)
                                    if time_match:
                                        minutes = int(time_match.group(1))
                                        seconds = int(time_match.group(2))
                                        total_seconds = minutes * 60 + seconds + 120
                                        logging.info(f"Waiting for {total_seconds} seconds before restarting...")
                                        await asyncio.sleep(total_seconds)
                                    else:
                                        logging.warning("Could not extract time from the message.")
                                        if retry_count >= max_retries:
                                            logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                                            await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                                            retry_count = 0  # إعادة تعيين عدد المحاولات
                                        retry_count += 1
                                        continue
                            else:
                                logging.warning("Bot did not respond with a new message.")
                                if retry_count >= max_retries:
                                    logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                                    await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                                    retry_count = 0  # إعادة تعيين عدد المحاولات
                                retry_count += 1
                                continue

                if not button_found:
                    logging.warning(f"Button '{button_text}' not found in the last message.")
                    if retry_count >= max_retries:
                        logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                        await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                        retry_count = 0  # إعادة تعيين عدد المحاولات
                    retry_count += 1
                    continue
            else:
                logging.warning("No buttons found in the last message.")
                if retry_count >= max_retries:
                    logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                    await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                    retry_count = 0  # إعادة تعيين عدد المحاولات
                retry_count += 1
                continue

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            if retry_count >= max_retries:
                logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                retry_count = 0  # إعادة تعيين عدد المحاولات
            retry_count += 1
            continue