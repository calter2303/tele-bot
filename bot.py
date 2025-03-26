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
    """Menjalankan bot Telegram dengan polling."""
    await application.initialize()
    await application.start()
    print("Telegram bot started!")
    await application.run_polling()

def run_flask():
    """Menjalankan Flask dengan Uvicorn."""
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

async def main():
    """Menjalankan Telegram bot dan Flask secara bersamaan."""
    telegram_task = asyncio.create_task(run_telegram())

    # Jalankan Flask secara async juga biar gak nge-block
    flask_task = asyncio.to_thread(run_flask)

    await asyncio.gather(telegram_task, flask_task)

if __name__ == "__main__":
    asyncio.run(main())  # ✅ FIX: Gunakan asyncio.run() untuk menjalankan kedua task bareng
