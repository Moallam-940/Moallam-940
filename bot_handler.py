async def handle_bot(target_bot_id, message, button_text):
    """
    دالة غير تزامنية (async) للتعامل مع البوت.
    """
    logging.info(f"جارٍ بدء التعامل مع البوت '{target_bot_id}'...")

    retry_count = 0  # عدد مرات إعادة المحاولة
    max_retries = 1  # الحد الأقصى لعدد المحاولات

    while True:
        try:
            logging.info(f"المحاولة رقم {retry_count + 1} للبوت '{target_bot_id}'...")

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
                if isinstance(dialog.entity, User) and dialog.entity.bot:
                    if dialog.entity.id == target_bot_id or dialog.name == target_bot_name:
                        target_bot = dialog.entity
                        break

            # إذا لم يتم العثور على البوت
            if not target_bot:
                logging.error(f"لم يتم العثور على البوت بإحدى المعرفات '{target_bot_id}' أو اسم المستخدم '{target_bot_name}'.")
                retry_count += 1  # زيادة عدد المحاولات

                if retry_count >= max_retries:
                    logging.warning("تم الوصول إلى الحد الأقصى للمحاولات. جاري الانتظار لمدة ساعة قبل إعادة المحاولة...")
                    await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                    retry_count = 0  # إعادة تعيين عدد المحاولات
                continue

            logging.info(f"تم العثور على البوت: {target_bot.username}")

            # تنفيذ باقي العمليات كما هو الحال في الكود السابق

        except Exception as e:
            logging.error(f"حدث خطأ: {e}")
            retry_count += 1  # زيادة عدد المحاولات

            if retry_count >= max_retries:
                logging.warning("تم الوصول إلى الحد الأقصى للمحاولات. جاري الانتظار لمدة ساعة قبل إعادة المحاولة...")
                await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                retry_count = 0  # إعادة تعيين عدد المحاولات
            continue
