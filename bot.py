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
    logger.info(f"Received /pay command from user {user_id}")

    if is_member(user_id):
        await update.message.reply_text("✅ You are already a member and your payment is confirmed!")
        return

    payment_link = create_payment_link(update.message.from_user, 1000)
    if payment_link:
        await update.message.reply_text(f"💳 Please complete your payment using this link: {payment_link}")
    else:
        await update.message.reply_text("❌ There was an error creating the payment link. Please try again later.")

async def main():
    # Pastikan Railway tidak mengalami error event loop
    nest_asyncio.apply()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("pay", start))

    # Set webhook
    webhook_url = f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"

    response = requests.post(url, json={"url": webhook_url})
    if response.status_code == 200:
        logger.info(f"✅ Webhook set: {webhook_url}")
    else:
        logger.error(f"❌ Webhook failed: {response.text}")

    logger.info(f"🚀 Bot is running on port {PORT}")

    await application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=webhook_url,
    )

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(main())  # Jalankan bot tanpa menutup event loop
        loop.run_forever()  # Pastikan loop tetap berjalan
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
