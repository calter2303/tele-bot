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

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.route("/")
def index():
    return "Bot is alive!"

async def run_telegram():
    """Jalankan polling bot Telegram tanpa menutup event loop."""
    await application.run_polling()

def main():
    """Menjalankan Flask dan Telegram dalam satu event loop tanpa asyncio.run()."""
    loop = asyncio.get_event_loop()

    # Jalankan bot Telegram dalam event loop
    loop.create_task(run_telegram())

    # Jalankan Flask menggunakan Uvicorn dalam event loop yang sama
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
