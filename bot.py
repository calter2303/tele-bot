import os
import logging
import asyncio
from flask import Flask
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import uvicorn

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = int(os.getenv("PORT", 8000))  # Railway pakai env PORT

# Setup logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Setup Flask
app = Flask(__name__)

# Setup Telegram bot
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Bot is running!")

async def echo(update: Update, context: CallbackContext):
    await update.message.reply_text(update.message.text)

# Tambahkan handler
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.route("/")
def index():
    return "Bot is alive!"

async def run_telegram():
    """Menjalankan bot Telegram dengan polling sebagai task terpisah."""
    await application.initialize()
    await application.start()
    logging.info("Telegram bot started!")
    await application.run_polling(stop_signals=None)  # Hindari penutupan event loop

async def run_flask():
    """Menjalankan Flask dengan Uvicorn di Railway."""
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    """Jalankan Telegram bot & Flask secara bersamaan."""
    telegram_task = asyncio.create_task(run_telegram())  
    flask_task = asyncio.create_task(run_flask())  
    await asyncio.gather(telegram_task, flask_task)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())  # ✅ Jalankan main() tanpa restart event loop
    loop.run_forever()  # ✅ Pastikan loop tetap berjalan
