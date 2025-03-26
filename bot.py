import os
import time
import json
import asyncio
import base64
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv

# Memuat variabel dari file .env
load_dotenv()

# Ambil variabel dari .env
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
MIDTRANS_SERVER_KEY = os.getenv('MIDTRANS_SERVER_KEY')
CHANNEL_ID = os.getenv('CHANNEL_ID')

# URL Midtrans untuk pembayaran
MIDTRANS_URL = "https://api.sandbox.midtrans.com/v2/charge"

# Database user membership (sementara pakai dict)
memberships = {}

async def start(update: Update, context: CallbackContext):
    """Menangani perintah /start"""
    await update.message.reply_text(
        "Halo! Selamat datang di Membership Bot 🚀\n"
        "Gunakan /buy untuk membeli akses."
    )

async def buy(update: Update, context: CallbackContext):
    """Menangani perintah /buy untuk pembayaran Midtrans"""
    user_id = update.message.chat_id
    amount = 15000  # Harga 15.000 IDR

    # Encode Server Key dengan Base64
    auth_key = base64.b64encode(f"{MIDTRANS_SERVER_KEY}:".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_key}",
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
        response = requests.post(MIDTRANS_URL, headers=headers, json=data)
        response_data = response.json()

        if response_data.get('status_code') == '201':
            payment_url = response_data["actions"][1]["url"]  # Deeplink GoPay
            await update.message.reply_text(f"✅ Silakan bayar dengan GoPay:\n{payment_url}")
        else:
            await update.message.reply_text("⚠️ Gagal membuat pembayaran, coba lagi nanti.")
    except Exception as e:
        await update.message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")

async def check_membership():
    """Cek membership secara berkala dan hapus pengguna yang masa berlakunya habis"""
    while True:
        expired_users = [user_id for user_id, expire_time in memberships.items() if time.time() > expire_time]

        for user_id in expired_users:
            try:
                await app.bot.ban_chat_member(CHANNEL_ID, user_id)
                del memberships[user_id]
                print(f"🚨 User {user_id} dihapus dari channel karena masa membership habis.")
            except Exception as e:
                print(f"❌ Gagal menghapus user {user_id}: {e}")

        await asyncio.sleep(86400)  # Cek setiap 24 jam

async def main():
    """Fungsi utama untuk menjalankan bot"""
    global app
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Tambahkan handler perintah
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))

    # Jalankan pengecekan membership di background
    asyncio.create_task(check_membership())

    # Jalankan bot
    await app.run_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
