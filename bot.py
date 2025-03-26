import os
import logging
import asyncio
import requests
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

# Initialize bot application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
application.initialize()  # Diperlukan agar process_update() berfungsi

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

application.add_handler(CommandHandler("pay", start))

# Set webhook function
def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"

    response = requests.post(url, json={"url": webhook_url})
    if response.status_code == 200:
        logger.info(f"✅ Webhook set: {webhook_url}")
    else:
        logger.error(f"❌ Webhook failed: {response.text}")

if __name__ == '__main__':
    set_webhook()
    logger.info(f"🚀 Bot is running on port {PORT}")

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}",
    )
