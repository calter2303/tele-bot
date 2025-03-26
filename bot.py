import os
import logging
import asyncio
from flask import Flask
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import threading
import uvicorn

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

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

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.route("/")
def index():
    return "Bot is alive!"

def run_telegram():
    """Menjalankan polling bot Telegram di thread terpisah."""
    asyncio.set_event_loop(asyncio.new_event_loop())  # Membuat event loop baru
    loop = asyncio.get_event_loop()
    loop.run_until_complete(application.run_polling())

def run_flask():
    """Menjalankan server Flask."""
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    # Menjalankan Telegram bot di thread terpisah
    telegram_thread = threading.Thread(target=run_telegram, daemon=True)
    telegram_thread.start()

    # Menjalankan Flask di thread utama
    run_flask()
