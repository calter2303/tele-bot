import os
import logging
import requests
import asyncio
import nest_asyncio
from flask import Flask, request, jsonify
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

# Pastikan database dibuat sebelum bot jalan
create_db()

# Fix event loop untuk Railway
nest_asyncio.apply()

# Setup Flask buat handle webhook
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    await application.update.update_queue.put(update)
    return jsonify({"status": "ok"})

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
    """Main function to run the bot with webhook"""
    global application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("pay", start))

    webhook_url = f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"

    logger.info(f"✅ Setting webhook: {webhook_url}")
    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook",
        json={"url": webhook_url}
    )

    if response.status_code == 200:
        logger.info(f"✅ Webhook set successfully: {webhook_url}")
    else:
        logger.error(f"❌ Webhook setup failed: {response.text}")

    logger.info(f"🚀 Bot is running on port {PORT}")

if __name__ == '__main__':
    asyncio.run(main())
