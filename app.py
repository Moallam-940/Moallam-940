from quart import Quart
from config import port

app = Quart(__name__)

@app.route('/')
async def home():
    logging.info("Home route accessed!")
    return "Service is running!"

async def run_app():
    logging.info("Starting Quart app...")
    await app.run_task(host='0.0.0.0', port=port)