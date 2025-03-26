import os
import logging
import asyncio
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv
from payment_service import create_payment_link
from membership_db import is_member, create_db

# Memuat variabel dari file .env
load_dotenv()

# Konfigurasi environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8080))

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Inisialisasi aplikasi bot
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Pastikan database dibuat saat startup
create_db()

# Fungsi untuk memulai proses pembayaran
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Cek apakah pengguna sudah menjadi member
    if is_member(user_id):
        await update.message.reply_text("✅ You are already a member and your payment is confirmed!")
        return

    # Buat link pembayaran
    payment_link = create_payment_link(update.message.from_user, 1000)
    if payment_link:
        await update.message.reply_text(f"💳 Please complete your payment using this link: {payment_link}")
    else:
        await update.message.reply_text("❌ There was an error creating the payment link. Please try again later.")

# Tambahkan handler untuk perintah /pay
application.add_handler(CommandHandler("pay", start))

# Setup Flask untuk menerima webhook
app = Flask(__name__)

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if not data:
            logging.warning("⚠️ Received empty request!")
            return 'No data received', 400
        
        update = Update.de_json(data, application.bot)
        logging.info(f"📩 Received update: {update}")
        
        # Proses update secara async
        asyncio.run(application.process_update(update))
    except Exception as e:
        logging.error(f"❌ Error processing update: {e}")
        return 'Error', 500

    return 'OK', 200

# Set webhook otomatis saat startup
def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"

    response = requests.post(url, json={"url": webhook_url})

    if response.status_code == 200:
        logging.info(f"✅ Webhook berhasil diatur: {webhook_url}")
    else:
        logging.error(f"❌ Gagal mengatur webhook: {response.text}")

if __name__ == '__main__':
    set_webhook()  # Pasang webhook otomatis saat bot start
    logging.info(f"🚀 Bot is running on port {PORT}")

    try:
        app.run(host='0.0.0.0', port=PORT)
    except Exception as e:
        logging.error(f"❌ Flask failed to start: {e}")
        logging.info("🛠 Switching to polling mode as a backup...")
        application.run_polling()
