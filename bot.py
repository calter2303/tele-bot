import os
import time
import json
import asyncio
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get variables from .env or Railway environment
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
MIDTRANS_SERVER_KEY = os.getenv('MIDTRANS_SERVER_KEY')
CHANNEL_ID = os.getenv('CHANNEL_ID')

# Midtrans API URL
MIDTRANS_URL = "https://api.sandbox.midtrans.com/v2/charge"

# Membership database (temporary dict)
memberships = {}

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Halo! Selamat datang di Membership Bot 🚀\nGunakan /buy untuk membeli akses.")

async def buy(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    amount = 15000  # Price: 15,000 IDR
    
    headers = {
        "Authorization": "Basic " + MIDTRANS_SERVER_KEY,
        "Content-Type": "application/json",
    }
    
    data = {
        "payment_type": "gopay",
        "transaction_details": {
            "order_id": f"ORDER-{user_id}-{int(time.time())}",
            "gross_amount": amount
        },
        "gopay": {
            "enable_callback": True,
            "callback_url": "https://example.com/callback"
        }
    }

    try:
        response = requests.post(MIDTRANS_URL, headers=headers, data=json.dumps(data))
        response_data = response.json()
        if response_data.get('status_code') == '201':
            payment_url = response_data["actions"][1]["url"]  # GoPay deeplink
            await update.message.reply_text(f"✅ Silakan bayar dengan GoPay:\n{payment_url}")
        else:
            await update.message.reply_text("❌ Gagal membuat pembayaran, coba lagi nanti.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Terjadi kesalahan: {str(e)}")

async def check_membership():
    while True:
        for user_id, expire_time in list(memberships.items()):
            if time.time() > expire_time:
                try:
                    await app.bot.ban_chat_member(CHANNEL_ID, user_id)
                    del memberships[user_id]
                except Exception as e:
                    print(f"⚠️ Gagal menghapus user {user_id}: {str(e)}")
        await asyncio.sleep(86400)  # Check every 24 hours

async def main():
    global app
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))

    # Run membership checker in background
    asyncio.create_task(check_membership())

    print("🤖 Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
