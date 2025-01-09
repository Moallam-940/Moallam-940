async def handle_bot(target_bot_name, message, button_text):
    logging.info(f"Starting handle_bot for {target_bot_name}...")
    retry_count = 0  # عدد مرات إعادة التشغيل
    max_retries = 1  # الحد الأقصى لعدد المحاولات

    while True:
        try:
            logging.info(f"Attempt {retry_count + 1} for {target_bot_name}...")

            # التحقق من أن العميل مصرح له بالاتصال
            if not await client.is_user_authorized():
                logging.error("Client is not authorized. Please check the session string.")
                await asyncio.sleep(3600)  # الانتظار لمدة ساعة قبل إعادة المحاولة
                continue

            # الحصول على الدردشات (المحادثات) المتاحة
            dialogs = await client.get_dialogs()
            logging.info(f"Found {len(dialogs)} dialogs.")

            target_bot = None
            for dialog in dialogs:
                if isinstance(dialog.entity, User) and dialog.entity.bot and dialog.name == target_bot_name:
                    target_bot = dialog.entity
                    break
                elif isinstance(dialog.entity, User) and dialog.entity.bot:
                    logging.info(f"Found bot: {dialog.name} (Username: {dialog.entity.username})")

            # إذا لم يتم العثور على البوت
            if not target_bot:
                logging.error(f"Bot with name '{target_bot_name}' not found.")
                retry_count += 1  # زيادة عدد المحاولات

                if retry_count >= max_retries:
                    logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                    await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                    retry_count = 0  # إعادة تعيين عدد المحاولات
                continue

            logging.info(f"Found bot: {target_bot.username}")

            # إرسال الرسالة إلى البوت
            logging.info(f"Sending message '{message}' to {target_bot.username}...")
            await client.send_message(target_bot.username, message)
            logging.info(f"Message '{message}' sent to {target_bot.username}!")

            # الانتظار لمدة 10 ثواني
            await asyncio.sleep(10)

            # الحصول على آخر رسالة من البوت
            messages = await client.get_messages(target_bot.username, limit=1)
            if not messages:
                logging.warning("No messages found in the chat.")
                retry_count += 1  # زيادة عدد المحاولات

                if retry_count >= max_retries:
                    logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                    await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                    retry_count = 0  # إعادة تعيين عدد المحاولات
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
                                        peer=target_bot.username,
                                        msg_id=last_message.id,
                                        data=button.data
                                    ))
                                    logging.info(f"Button '{button.text}' clicked!")
                                except Exception as e:
                                    logging.error(f"Failed to receive response after clicking button: {e}")
                                    retry_count += 1  # زيادة عدد المحاولات

                                    if retry_count >= max_retries:
                                        logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                                        await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                                        retry_count = 0  # إعادة تعيين عدد المحاولات
                                    continue

                            # الانتظار لمدة 10 ثواني بعد النقر على الزر
                            await asyncio.sleep(10)

                            # الحصول على الرسائل الجديدة بعد النقر على الزر
                            new_messages = await client.get_messages(target_bot.username, limit=1)
                            if new_messages and new_messages[0].id != last_message.id:
                                logging.info("Bot responded with a new message.")
                                logging.info(f"Bot's response: {new_messages[0].text}")

                                # التحقق من وجود العبارة المطلوبة في الرسالة الجديدة
                                if "next available bonus" not in new_messages[0].text:
                                    logging.warning("'next available bonus' not found in the message.")
                                    retry_count += 1  # زيادة عدد المحاولات

                                    if retry_count >= max_retries:
                                        logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                                        await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                                        retry_count = 0  # إعادة تعيين عدد المحاولات
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
                                        retry_count += 1  # زيادة عدد المحاولات

                                        if retry_count >= max_retries:
                                            logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                                            await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                                            retry_count = 0  # إعادة تعيين عدد المحاولات
                                        continue
                            else:
                                logging.warning("Bot did not respond with a new message.")
                                retry_count += 1  # زيادة عدد المحاولات

                                if retry_count >= max_retries:
                                    logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                                    await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                                    retry_count = 0  # إعادة تعيين عدد المحاولات
                                continue

                if not button_found:
                    logging.warning(f"Button '{button_text}' not found in the last message.")
                    retry_count += 1  # زيادة عدد المحاولات

                    if retry_count >= max_retries:
                        logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                        await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                        retry_count = 0  # إعادة تعيين عدد المحاولات
                    continue
            else:
                logging.warning("No buttons found in the last message.")
                retry_count += 1  # زيادة عدد المحاولات

                if retry_count >= max_retries:
                    logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                    await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                    retry_count = 0  # إعادة تعيين عدد المحاولات
                continue

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            retry_count += 1  # زيادة عدد المحاولات

            if retry_count >= max_retries:
                logging.warning("Max retries reached. Waiting for 1 hour before retrying...")
                await asyncio.sleep(3600)  # الانتظار لمدة ساعة
                retry_count = 0  # إعادة تعيين عدد المحاولات
            continue