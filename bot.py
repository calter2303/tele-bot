import os
import time
import json
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler

# Ambil token bot dari environment variable
TOKEN = os.getenv("7654581013:AAFcKVBMI5631hzxLdI8myDrw_1BISLISH0")
CHANNEL_ID = os.getenv(-1002405572136)  # ID Channel Private
MIDTRANS_SERVER_KEY = os.getenv("SB-Mid-server-8PDelYjTLlz2kCg2lMnnlQDR")
MIDTRANS_URL = "https://api.sandbox.midtrans.com/v2/charge"  # Ganti ke production nanti

app = Flask(__name__)
bot_app = Application.builder().token(TOKEN).build()

# Simpan membership sementara (idealnya pakai database)
memberships = {}

async def start(update: Update, context):
    """Pesan saat user mulai chat dengan bot"""
    await update.message.reply_text("Halo! Gunakan /buy untuk membeli akses.")

async def buy(update: Update, context):
    """User beli akses, bot buat QRIS"""
    user_id = update.message.chat_id
    order_id = f"ORDER-{user_id}-{int(time.time())}"
    
    data = {
        "payment_type": "qris",
        "transaction_details": {"order_id": order_id, "gross_amount": 15000},
        "qris": {"acquirer": "gopay"},
        "customer_details": {"first_name": "User", "email": "user@example.com"}
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + requests.auth._basic_auth_str(MIDTRANS_SERVER_KEY, "")
    }

    response = requests.post(MIDTRANS_URL, headers=headers, data=json.dumps(data))
    result = response.json()

    if result.get("status_code") == "201":
        qris_url = result["actions"][0]["url"]
        memberships[user_id] = {"order_id": order_id, "time": time.time()}
        await update.message.reply_text(f"Silakan scan QRIS ini untuk membayar: {qris_url}")
    else:
        await update.message.reply_text("Gagal membuat QRIS. Coba lagi nanti.")

@app.route("/webhook", methods=["POST"])
def webhook():
    """Webhook Midtrans untuk cek pembayaran"""
    data = request.get_json()
    order_id = data.get("order_id")
    transaction_status = data.get("transaction_status")

    for user_id, info in memberships.items():
        if info["order_id"] == order_id and transaction_status == "settlement":
            # User berhasil bayar, invite ke channel
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/inviteChatMember",
                json={"chat_id": CHANNEL_ID, "user_id": user_id}
            )
            return "OK", 200

    return "Ignored", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
