import os
import logging
import nest_asyncio
import asyncio
from threading import Thread
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler
from dotenv import load_dotenv
from payment_service import create_payment_link
from membership_db import is_member, create_db

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8080))

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN tidak ditemukan di environment variables!")

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Pastikan database dibuat sebelum bot jalan
try:
    create_db()
    logger.info("✅ Database initialized successfully")
except Exception as e:
    logger.error(f"❌ Database initialization failed: {e}", exc_info=True)

# Fix event loop untuk Railway
nest_asyncio.apply()

# Setup Flask untuk handle webhook
app = Flask(__name__)

# Inisialisasi bot Telegram
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    """Handler untuk menerima update dari Telegram via webhook."""
    try:
        json_data = request.get_json()
        if not json_data:
            logger.warning("⚠️ Received empty request payload!")
            return jsonify({"status": "error", "message": "Empty payload"}), 400

        update = Update.de_json(json_data, application.bot)

        # Proses update secara asinkron agar Flask tidak terganggu
        loop = asyncio.get_event_loop()
        loop.create_task(application.update_queue.put(update))

        logger.info(f"✅ Update diterima dari Telegram: {update}")

        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"❌ Error handling webhook: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

async def start(update: Update, context):
    """Command /pay untuk membuat link pembayaran."""
    user_id = update.message.from_user.id
    logger.info(f"💰 Received /pay command from user {user_id}")

    if is_member(user_id):
        await update.message.reply_text("✅ You are already a member and your payment is confirmed!")
        return

    payment_link = create_payment_link(update.message.from_user, 1000)
    if payment_link:
        await update.message.reply_text(f"💳 Please complete your payment using this link: {payment_link}")
    else:
        await update.message.reply_text("❌ There was an error creating the payment link. Please try again later.")

async def welcome(update: Update, context):
    """Command /start untuk menyambut pengguna baru."""
    user_id = update.message.from_user.id
    logger.info(f"👋 Received /start command from user {user_id}")
    await update.message.reply_text("👋 Welcome! Use /pay to get the payment link.")

async def set_webhook():
    """Fungsi untuk mengatur webhook."""
    if WEBHOOK_URL:
        webhook_url = f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
        logger.info(f"✅ Setting webhook: {webhook_url}")

        try:
            await application.bot.set_webhook(webhook_url)
            logger.info(f"✅ Webhook set successfully: {webhook_url}")
        except Exception as e:
            logger.error(f"❌ Webhook setup failed: {e}", exc_info=True)
    else:
        logger.warning("⚠️ WEBHOOK_URL tidak diset! Bot akan berjalan dengan polling mode.")

def run_flask():
    """Jalankan Flask server di thread terpisah."""
    logger.info(f"🚀 Running Flask server on port {PORT}")
    try:
        app.run(host="0.0.0.0", port=PORT, use_reloader=False)
    except Exception as e:
        logger.error(f"❌ Flask error: {e}", exc_info=True)

async def run_bot():
    """Jalankan bot dengan polling kalau webhook tidak diaktifkan."""
    application.add_handler(CommandHandler("start", welcome))
    application.add_handler(CommandHandler("pay", start))

    await application.initialize()

    if WEBHOOK_URL:
        await set_webhook()
        flask_thread = Thread(target=run_flask, daemon=True)
        flask_thread.start()
        await application.start()
        await asyncio.Future()  # Menjaga bot tetap berjalan
    else:
        logger.info("🚀 Running bot in polling mode")
        await application.run_polling()

async def shutdown():
    """Fungsi untuk menutup bot dengan bersih saat dihentikan."""
    logger.info("🛑 Shutting down bot...")
    try:
        await application.shutdown()
        logger.info("✅ Bot stopped successfully!")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}", exc_info=True)

if __name__ == '__main__':
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("🛑 KeyboardInterrupt detected! Shutting down...")
        asyncio.run(shutdown())
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
    finally:
        logger.info("✅ Bot exited cleanly.")
