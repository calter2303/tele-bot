import os
import asyncio
import logging
import threading
from flask import Flask, request
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Setup Flask
app = Flask(__name__)

# Setup logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Setup Telegram bot
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Bot is running!")

async def echo(update: Update, context: CallbackContext):
    await update.message.reply_text(update.message.text)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

async def run_bot():
    """Jalankan bot Telegram dalam mode polling."""
    await application.run_polling()

@app.route("/")
def index():
    return "Bot is alive!"

if __name__ == "__main__":
    # Jalankan bot Telegram di thread terpisah
    bot_thread = threading.Thread(target=lambda: asyncio.run(run_bot()))
    bot_thread.start()

    # Jalankan Flask dengan Uvicorn (untuk Railway)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
