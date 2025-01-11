import logging
import asyncio
import re
from telethon import functions
from telethon.tl.types import User, KeyboardButtonCallback
from telegram_client import client

# تهيئة السجل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def handle_bot(target_bot_name, message, button_text):
    """
    دالة غير تزامنية (async) للتعامل مع البوت.
    """
    logging.info(f"جارٍ بدء التعامل مع البوت '{target_bot_name}'...")
    retry_count = 0  # عدد مرات إعادة المحاولة
    max_retries = 1  # الحد الأقصى لعدد المحاولات

    while True:
        try:
            logging.info(f"المحاولة رقم {retry_count + 1} للبوت '{target_bot_name}'...")

            # التحقق من أن العميل متصل
            if not client.is_connected():
                logging.info("جارٍ توصيل العميل...")
                await client.connect()

            # التحقق من أن العميل مصرح له بالاتصال
            if not await client.is_user_authorized():
                logging.error("العميل غير مصرح له. يرجى التحقق من جلسة العمل.")
                await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة المحاولة
                continue

            # الحصول على الدردشات (المحادثات) المتاحة
            dialogs = await client.get_dialogs()
            logging.info(f"تم العثور على {len(dialogs)} دردشة.")

            target_bot = None
            for dialog in dialogs:
                if isinstance(dialog.entity, User) and dialog.entity.bot and dialog.name == target_bot_name:
                    target_bot = dialog.entity
                    break

            # إذا لم يتم العثور على البوت
            if not target_bot:
                logging.error(f"لم يتم العثور على البوت باسم '{target_bot_name}'.")
                retry_count += 1  # زيادة عدد المحاولات

                if retry_count >= max_retries:
                    logging.warning("تم الوصول إلى الحد الأقصى للمحاولات. جاري الانتظار لمدة ساعة قبل إعادة المحاولة...")
                    await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                    retry_count = 0  # إعادة تعيين عدد المحاولات
                continue

            logging.info(f"تم العثور على البوت: {target_bot.username}")

            # إرسال الرسالة إلى البوت
            logging.info(f"جارٍ إرسال الرسالة '{message}' إلى {target_bot.username}...")
            await client.send_message(target_bot.username, message)
            logging.info(f"تم إرسال الرسالة '{message}' إلى {target_bot.username}!")

            # الانتظار لمدة 10 ثواني
            await asyncio.sleep(10)

            # محاولة الحصول على آخر رسالة من البوت
            try:
                messages = await client.get_messages(target_bot.username, limit=1)
                if not messages:
                    logging.warning("لم يتم العثور على رسائل في الدردشة.")
                    raise Exception("لم يتم العثور على رسائل في الدردشة.")
            except Exception as e:
                logging.error(f"فشل في الحصول على الرسائل: {e}")
                retry_count += 1  # زيادة عدد المحاولات

                if retry_count >= max_retries:
                    logging.warning("تم الوصول إلى الحد الأقصى للمحاولات. جاري الانتظار لمدة ساعة قبل إعادة المحاولة...")
                    await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                    retry_count = 0  # إعادة تعيين عدد المحاولات
                continue

            last_message = messages[0]
            logging.info(f"آخر رسالة من البوت: {last_message.text}")

            # البحث عن الزر والضغط عليه (فقط إذا كان button_text ليس "0")
            if button_text != "0" and last_message.reply_markup:
                button_found = False
                for row in last_message.reply_markup.rows:
                    for button in row.buttons:
                        if button_text in button.text:
                            logging.info(f"تم العثور على الزر: {button_text} في البوت {target_bot.username}!")
                            button_found = True

                            # الضغط على الزر
                            if isinstance(button, KeyboardButtonCallback):
                                try:
                                    await client(functions.messages.GetBotCallbackAnswerRequest(
                                        peer=target_bot.username,
                                        msg_id=last_message.id,
                                        data=button.data
                                    ))
                                    logging.info(f"تم النقر على الزر '{button.text}' في البوت {target_bot.username}!")
                                except Exception as e:
                                    logging.error(f"فشل في النقر على الزر: {e}")
                                    raise e

                            # الانتظار لمدة 10 ثواني بعد النقر على الزر (دون انتظار رد)
                            await asyncio.sleep(10)
                            break  # الخروج من الحلقة بعد النقر على الزر

                    if button_found:
                        break  # الخروج من الحلقة الخارجية بعد النقر على الزر

                if not button_found:
                    logging.warning(f"لم يتم العثور على الزر '{button_text}' في الرسالة الأخيرة.")
                    raise Exception(f"لم يتم العثور على الزر '{button_text}' في الرسالة الأخيرة.")
            else:
                logging.info("تم تخطي النقر على الزر لأن button_text == '0'.")

            # محاولة استخراج الوقت من الرسالة
            try:
                time_match = re.search(
                    r"(?:(\d+)\s*Hours?)?\s*(?:(\d+)\s*Minutes?)?\s*(?:(\d+)\s*Seconds?)?",
                    last_message.text,
                    re.IGNORECASE
                )
                if time_match:
                    hours = int(time_match.group(1) or 0)
                    minutes = int(time_match.group(2) or 0)
                    seconds = int(time_match.group(3) or 0)
                    total_seconds = (hours * 3600) + (minutes * 60) + seconds
                    logging.info(f"جارٍ الانتظار لمدة {total_seconds} ثانية ({hours} ساعات، {minutes} دقائق، {seconds} ثواني) قبل إعادة التشغيل...")
                    await asyncio.sleep(total_seconds)
                else:
                    # إذا لم يتم العثور على الوقت في الرسالة
                    if button_text == "0":
                        total_seconds = 86400  # 24 ساعة
                        logging.info(f"جارٍ الانتظار لمدة {total_seconds} ثانية (24 ساعة) قبل إعادة التشغيل...")
                    else:
                        total_seconds = 3600  # ساعة واحدة
                        logging.info(f"جارٍ الانتظار لمدة {total_seconds} ثانية (ساعة واحدة) قبل إعادة التشغيل...")
                    await asyncio.sleep(total_seconds)
            except Exception as e:
                logging.error(f"حدث خطأ أثناء استخراج الوقت: {e}")
                raise e

        except Exception as e:
            logging.error(f"حدث خطأ: {e}")
            retry_count += 1  # زيادة عدد المحاولات

            if retry_count >= max_retries:
                logging.warning("تم الوصول إلى الحد الأقصى للمحاولات. جاري الانتظار لمدة ساعة قبل إعادة المحاولة...")
                await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                retry_count = 0  # إعادة تعيين عدد المحاولات
            continue