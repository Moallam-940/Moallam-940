import os

# إعدادات التطبيق والمتغيرات البيئية
api_id = os.getenv('API_ID')  # معرف API الخاص بـ Telegram
api_hash = os.getenv('API_HASH')  # هاش API الخاص بـ Telegram
session_string = os.getenv('SESSION_STRING')  # سلسلة الجلسة للاتصال بـ Telegram
port = int(os.getenv('PORT', 8080))  # المنفذ الذي سيعمل عليه التطبيق (الافتراضي 8080)