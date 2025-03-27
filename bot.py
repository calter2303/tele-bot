import os
import logging
import requests
import asyncio
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

# Command /pay
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

# Fungsi utama untuk menjalankan bot dengan webhook
async def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("pay", start))

    webhook_url = f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
    logger.info(f"🚀 Bot is running on port {PORT}")

    await application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=webhook_url,
    )

# Fungsi untuk set webhook
async def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"

    for attempt in range(5):
        response = requests.post(url, json={"url": webhook_url})
        if response.status_code == 200:
            logger.info(f"✅ Webhook set successfully: {webhook_url}")
            return
        elif response.status_code == 429:
            retry_after = response.json().get("parameters", {}).get("retry_after", 1)
            logger.warning(f"⚠️ Too many requests. Retrying in {retry_after} seconds...")
            await asyncio.sleep(retry_after)
        else:
            logger.error(f"❌ Webhook failed: {response.text}")
            break

# Jalankan bot
async def run():
    await set_webhook()
    await main()

if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run())
    else:
        loop.create_task(run())
