import os
import logging
import asyncio
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 🔹 Load Environment Variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
MIDTRANS_SERVER_KEY = os.getenv("MIDTRANS_SERVER_KEY")

# 🔹 Setup Logging
logging.basicConfig(level=logging.INFO)

# 🔹 Flask App
app = Flask(__name__)

# 🔹 Telegram Bot Setup
bot = Bot(token=TOKEN)

async def start(update: Update, context: CallbackContext):
    """Handler untuk command /start"""
    await update.message.reply_text("Halo! Selamat datang di bot kami.")

async def handle_message(update: Update, context: CallbackContext):
    """Handler untuk pesan teks biasa"""
    text = update.message.text
    await update.message.reply_text(f"Kamu mengirim: {text}")

# 🔹 Setup Telegram Bot dengan Async Application
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route("/", methods=["GET"])
def home():
    return "Bot Telegram dengan Midtrans 🚀"

@app.route("/midtrans-webhook", methods=["POST"])
def midtrans_webhook():
    """Handle webhook dari Midtrans"""
    data = request.json
    logging.info(f"Webhook Midtrans: {data}")

    # Kirim notifikasi ke Telegram
    status = data.get("transaction_status", "UNKNOWN")
    order_id = data.get("order_id", "No Order ID")
    payment_type = data.get("payment_type", "No Payment Type")

    message = f"🔔 Pembayaran Masuk!\n📌 Order ID: {order_id}\n💳 Status: {status}\n🛠 Metode: {payment_type}"
    
    # Kirim ke Telegram Channel
    asyncio.run(bot.send_message(chat_id=CHANNEL_ID, text=message))
    
    return jsonify({"status": "ok"}), 200

async def run_bot():
    """Menjalankan bot Telegram secara async"""
    await application.run_polling()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())
