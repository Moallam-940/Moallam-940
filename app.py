from quart import Quart
from config import port

# إنشاء تطبيق Quart
app = Quart(__name__)

@app.route('/')
async def home():
    """
    دالة للصفحة الرئيسية للتطبيق.
    """
    return "Service is running!"

async def run_app():
    """
    دالة لتشغيل تطبيق Quart.
    """
    await app.run_task(host='0.0.0.0', port=port)