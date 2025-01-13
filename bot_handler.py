import logging
import asyncio
import re
from telethon import functions
from telethon.tl.types import User, KeyboardButtonCallback
from telegram_client import client

# تهيئة السجل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def handle_bot(target_bot_username, message, button_text):
    """
    دالة غير تزامنية للتعامل مع البوت.
    """
    logging.info(f"جارٍ بدء التعامل مع البوت '{target_bot_username}'...")
    report = {
        "bot_username": target_bot_username,
        "message_sent": message,
        "button_clicked": button_text if button_text != "0" else "No button interaction",
        "wait_duration": 0  # سيتم تحديثها لاحقًا
    }

    try:
        # التأكد من أن العميل متصل
        if not client.is_connected():
            logging.info("جارٍ توصيل العميل...")
            await client.connect()

        # التأكد من أن العميل مصرح له
        if not await client.is_user_authorized():
            logging.error("العميل غير مصرح له. يرجى التحقق من جلسة العمل.")
            await asyncio.sleep(3600)  # الانتظار لمدة ساعة
            return

        # البحث عن البوت
        dialogs = await client.get_dialogs()
        logging.info(f"تم العثور على {len(dialogs)} دردشة.")

        target_bot = None
        for dialog in dialogs:
            if isinstance(dialog.entity, User) and dialog.entity.bot and dialog.entity.username == target_bot_username:
                target_bot = dialog.entity
                break

        if not target_bot:
            logging.error(f"لم يتم العثور على البوت باسم المستخدم '{target_bot_username}'.")
            return

        logging.info(f"تم العثور على البوت: {target_bot.username}")

        # إرسال الرسالة إلى البوت
        try:
            logging.info(f"جارٍ إرسال الرسالة '{message}' إلى {target_bot.username}...")
            await client.send_message(target_bot.username, message)
            logging.info(f"تم إرسال الرسالة '{message}' إلى {target_bot.username}!")
        except Exception as e:
            logging.error(f"حدث خطأ أثناء إرسال الرسالة: {e}")
            logging.info("جارٍ الانتظار لمدة ساعة قبل إعادة المحاولة...")
            await asyncio.sleep(3600)  # الانتظار لمدة ساعة
            return

        # انتظار 10 ثوانٍ
        await asyncio.sleep(10)

        # جلب الرسالة الأخيرة
        messages = await client.get_messages(target_bot.username, limit=1)
        if not messages:
            logging.warning("لم يتم العثور على رسائل في الدردشة.")
            return

        last_message = messages[0]
        logging.info(f"آخر رسالة من البوت: {last_message.text}")

        # التعامل مع الأزرار إذا وُجدت
        if last_message.reply_markup:
            button_found = False
            for row in last_message.reply_markup.rows:
                for button in row.buttons:
                    if button_text in button.text:  # التحقق من النص المطلوب
                        logging.info(f"تم العثور على الزر: {button.text}. جارٍ النقر عليه...")
                        button_found = True

                        # الضغط على الزر إذا كان قابلاً للنقر
                        if isinstance(button, KeyboardButtonCallback):
                            try:
                                await client(functions.messages.GetBotCallbackAnswerRequest(
                                    peer=target_bot.username,
                                    msg_id=last_message.id,
                                    data=button.data
                                ))
                                logging.info(f"تم النقر على الزر: {button.text}")
                            except Exception as e:
                                logging.error(f"فشل في النقر على الزر: {e}")

                        # الانتظار 10 ثوانٍ بعد النقر
                        await asyncio.sleep(10)
                        break

                if button_found:
                    break

            if not button_found:
                logging.warning(f"لم يتم العثور على الزر '{button_text}' في الرسالة الأخيرة.")
        else:
            logging.info("لا توجد أزرار في الرسالة الأخيرة.")

        # استخراج التوقيت
        try:
            time_match = re.search(
                r"(\d+)\s*hours?,\s*(\d+)\s*minutes?,\s*(\d+)\s*seconds?",
                last_message.text,
                re.IGNORECASE
            )
            if time_match:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                seconds = int(time_match.group(3))
                total_seconds = (hours * 3600) + (minutes * 60) + seconds
                logging.info(f"جارٍ الانتظار لمدة {total_seconds} ثانية ({hours} ساعات، {minutes} دقائق، {seconds} ثواني).")
            else:
                total_seconds = 3600  # ساعة افتراضية
                logging.info(f"لم يتم العثور على توقيت. سيتم الانتظار لمدة {total_seconds} ثانية.")
        except Exception as e:
            logging.error(f"حدث خطأ أثناء استخراج الوقت: {e}")
            total_seconds = 3600
            logging.info(f"تم تعيين مهلة افتراضية لمدة {total_seconds} ثانية.")

        report["wait_duration"] = total_seconds
        await asyncio.sleep(total_seconds)

    except Exception as e:
        logging.error(f"حدث خطأ: {e}")

    finally:
        # طباعة التقرير النهائي
        logging.info(f"تقرير العملية:\n"
                     f"- اسم البوت: {report['bot_username']}\n"
                     f"- الرسالة المرسلة: {report['message_sent']}\n"
                     f"- الزر الذي تم التفاعل معه: {report['button_clicked']}\n"
                     f"- مدة الانتظار: {report['wait_duration']} ثانية.")
