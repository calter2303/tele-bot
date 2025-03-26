import os
import logging
import requests
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv
from payment_service import create_payment_link
from membership_db import is_member, create_db

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8080))

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Ensure database is created
create_db()

# Payment command
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if is_member(user_id):
        await update.message.reply_text("✅ You are already a member and your payment is confirmed!")
        return

    payment_link = create_payment_link(update.message.from_user, 1000)
    if payment_link:
        await update.message.reply_text(f"💳 Please complete your payment using this link: {payment_link}")
    else:
        await update.message.reply_text("❌ There was an error creating the payment link. Please try again later.")

async def set_webhook(application: Application):
    """Cek apakah webhook sudah ada sebelum mengaturnya ulang."""
    webhook_url = f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
    
    # Cek webhook yang sudah terdaftar
    check_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"
    response = requests.get(check_url).json()

    if response.get("result") and response["result"].get("url") == webhook_url:
        logger.info(f"✅ Webhook sudah diset ke: {webhook_url}")
    else:
        logger.info("🔄 Mengatur webhook baru...")
        set_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
        res = requests.post(set_url, json={"url": webhook_url})
        if res.status_code == 200:
            logger.info(f"✅ Webhook berhasil diatur: {webhook_url}")
        else:
            logger.error(f"❌ Gagal mengatur webhook: {res.text}")

async def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    await application.initialize()

    application.add_handler(CommandHandler("pay", start))

    # Set webhook hanya jika belum ada
    await set_webhook(application)

    logger.info(f"🚀 Bot is running on port {PORT}")
    
    await application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}",
    )

# ✅ Perbaikan utama agar Railway tidak error
if __name__ == '__main__':
    nest_asyncio.apply()  # Hindari error event loop

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
