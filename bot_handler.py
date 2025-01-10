import logging
import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from telethon import functions
from telethon.tl.types import User, KeyboardButtonCallback
from telegram_client import client

# تهيئة السجل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def handle_bot_sync(target_bot_name, message, button_text):
    """
    دالة تزامنية (synchronous) للتعامل مع البوت.
    """
    logging.info(f"جارٍ بدء التعامل مع البوت '{target_bot_name}'...")
    retry_count = 0  # عدد مرات إعادة المحاولة
    max_retries = 1  # الحد الأقصى لعدد المحاولات

    while True:
        try:
            logging.info(f"المحاولة رقم {retry_count + 1} للبوت '{target_bot_name}'...")

            # التحقق من أن العميل مصرح له بالاتصال
            if not asyncio.run(client.is_user_authorized()):  # استخدام asyncio.run
                logging.error("العميل غير مصرح له. يرجى التحقق من جلسة العمل.")
                import time
                time.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة المحاولة
                continue

            # الحصول على الدردشات (المحادثات) المتاحة
            dialogs = asyncio.run(client.get_dialogs())  # استخدام asyncio.run
            logging.info(f"تم العثور على {len(dialogs)} دردشة.")

            target_bot = None
            for dialog in dialogs:
                if isinstance(dialog.entity, User) and dialog.entity.bot and dialog.name == target_bot_name:
                    target_bot = dialog.entity
                    break
                elif isinstance(dialog.entity, User) and dialog.entity.bot:
                    logging.info(f"تم العثور على بوت: {dialog.name} (اسم المستخدم: {dialog.entity.username})")

            # إذا لم يتم العثور على البوت
            if not target_bot:
                logging.error(f"لم يتم العثور على البوت باسم '{target_bot_name}'.")
                retry_count += 1  # زيادة عدد المحاولات

                if retry_count >= max_retries:
                    logging.warning("تم الوصول إلى الحد الأقصى للمحاولات. جاري الانتظار لمدة ساعة قبل إعادة المحاولة...")
                    import time
                    time.sleep(3600)  # الانتظار لمدة ساعة
                    retry_count = 0  # إعادة تعيين عدد المحاولات
                continue

            logging.info(f"تم العثور على البوت: {target_bot.username}")

            # إرسال الرسالة إلى البوت
            logging.info(f"جارٍ إرسال الرسالة '{message}' إلى {target_bot.username}...")
            asyncio.run(client.send_message(target_bot.username, message))  # استخدام asyncio.run
            logging.info(f"تم إرسال الرسالة '{message}' إلى {target_bot.username}!")

            # الانتظار لمدة 10 ثواني
            import time
            time.sleep(10)

            # الحصول على آخر رسالة من البوت
            messages = asyncio.run(client.get_messages(target_bot.username, limit=1))  # استخدام asyncio.run
            if not messages:
                logging.warning("لم يتم العثور على رسائل في الدردشة.")
                retry_count += 1  # زيادة عدد المحاولات

                if retry_count >= max_retries:
                    logging.warning("تم الوصول إلى الحد الأقصى للمحاولات. جاري الانتظار لمدة ساعة قبل إعادة المحاولة...")
                    time.sleep(3600)  # الانتظار لمدة ساعة
                    retry_count = 0  # إعادة تعيين عدد المحاولات
                continue

            last_message = messages[0]
            logging.info(f"آخر رسالة من البوت: {last_message.text}")

            # البحث عن الزر المطلوب في الرسالة الأخيرة
            if last_message.reply_markup:
                button_found = False
                for row in last_message.reply_markup.rows:
                    for button in row.buttons:
                        if button_text in button.text:
                            logging.info(f"تم العثور على الزر: {button_text}")
                            button_found = True

                            # الضغط على الزر
                            if isinstance(button, KeyboardButtonCallback):
                                try:
                                    asyncio.run(client(functions.messages.GetBotCallbackAnswerRequest(
                                        peer=target_bot.username,
                                        msg_id=last_message.id,
                                        data=button.data
                                    )))  # استخدام asyncio.run
                                    logging.info(f"تم النقر على الزر '{button.text}'!")
                                except Exception as e:
                                    logging.error(f"فشل في تلقي الرد بعد النقر على الزر: {e}")
                                    
                            # الانتظار لمدة 10 ثواني بعد النقر على الزر
                            time.sleep(10)

                            # الحصول على الرسائل الجديدة بعد النقر على الزر
                            new_messages = asyncio.run(client.get_messages(target_bot.username, limit=1))  # استخدام asyncio.run
                            if new_messages and new_messages[0].id != last_message.id:
                                logging.info("رد البوت برسالة جديدة.")
                                logging.info(f"رد البوت: {new_messages[0].text}")

                                # التحقق من وجود العبارة المطلوبة في الرسالة الجديدة
                                if "next available bonus" not in new_messages[0].text:
                                    logging.warning("لم يتم العثور على 'next available bonus' في الرسالة.")
                                    retry_count += 1  # زيادة عدد المحاولات

                                    if retry_count >= max_retries:
                                        logging.warning("تم الوصول إلى الحد الأقصى للمحاولات. جاري الانتظار لمدة ساعة قبل إعادة المحاولة...")
                                        time.sleep(3600)  # الانتظار لمدة ساعة
                                        retry_count = 0  # إعادة تعيين عدد المحاولات
                                    continue
                                else:
                                    # استخراج الوقت من الرسالة
                                    time_match = re.search(r"(\d+)\s*Minute\s*(\d+)\s*Second", new_messages[0].text)
                                    if time_match:
                                        minutes = int(time_match.group(1))
                                        seconds = int(time_match.group(2))
                                        total_seconds = minutes * 60 + seconds + 120
                                        logging.info(f"جارٍ الانتظار لمدة {total_seconds} ثانية قبل إعادة التشغيل...")
                                        time.sleep(total_seconds)
                                    else:
                                        logging.warning("تعذر استخراج الوقت من الرسالة.")
                                        retry_count += 1  # زيادة عدد المحاولات

                                        if retry_count >= max_retries:
                                            logging.warning("تم الوصول إلى الحد الأقصى للمحاولات. جاري الانتظار لمدة ساعة قبل إعادة المحاولة...")
                                            time.sleep(3600)  # الانتظار لمدة ساعة
                                            retry_count = 0  # إعادة تعيين عدد المحاولات
                                        continue
                            else:
                                logging.warning("لم يرد البوت برسالة جديدة.")
                                retry_count += 1  # زيادة عدد المحاولات

                                if retry_count >= max_retries:
                                    logging.warning("تم الوصول إلى الحد الأقصى للمحاولات. جاري الانتظار لمدة ساعة قبل إعادة المحاولة...")
                                    time.sleep(3600)  # الانتظار لمدة ساعة
                                    retry_count = 0  # إعادة تعيين عدد المحاولات
                                continue

                if not button_found:
                    logging.warning(f"لم يتم العثور على الزر '{button_text}' في الرسالة الأخيرة.")
                    retry_count += 1  # زيادة عدد المحاولات

                    if retry_count >= max_retries:
                        logging.warning("تم الوصول إلى الحد الأقصى للمحاولات. جاري الانتظار لمدة ساعة قبل إعادة المحاولة...")
                        time.sleep(3600)  # الانتظار لمدة ساعة
                        retry_count = 0  # إعادة تعيين عدد المحاولات
                    continue
            else:
                logging.warning("لم يتم العثور على أزرار في الرسالة الأخيرة.")
                retry_count += 1  # زيادة عدد المحاولات

                if retry_count >= max_retries:
                    logging.warning("تم الوصول إلى الحد الأقصى للمحاولات. جاري الانتظار لمدة ساعة قبل إعادة المحاولة...")
                    time.sleep(3600)  # الانتظار لمدة ساعة
                    retry_count = 0  # إعادة تعيين عدد المحاولات
                continue

        except Exception as e:
            logging.error(f"حدث خطأ: {e}")
            retry_count += 1  # زيادة عدد المحاولات

            if retry_count >= max_retries:
                logging.warning("تم الوصول إلى الحد الأقصى للمحاولات. جاري الانتظار لمدة ساعة قبل إعادة المحاولة...")
                import time
                time.sleep(3600)  # الانتظار لمدة ساعة
                retry_count = 0  # إعادة تعيين عدد المحاولات
            continue

async def handle_bot(target_bot_name, message, button_text):
    """
    دالة غير تزامنية (asynchronous) لتشغيل المهمة في خيط منفصل.
    """
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        await loop.run_in_executor(executor, handle_bot_sync, target_bot_name, message, button_text)