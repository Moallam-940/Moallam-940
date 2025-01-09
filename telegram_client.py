from telethon import TelegramClient
from telethon.sessions import StringSession
from config import api_id, api_hash, session_string

# إنشاء عميل Telegram باستخدام سلسلة الجلسة
client = TelegramClient(StringSession(session_string), api_id, api_hash)