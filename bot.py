import os
import time
import json
import asyncio
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv

# Memuat variabel dari file .env
load_dotenv()

# Ambil variabel dari environment variables (Railway atau lokal)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
MIDTRANS_SERVER_KEY = os.getenv('MIDTRANS_SERVER_KEY')
CHANNEL_ID = os.getenv('CHANNEL_ID')

# URL Midtrans untuk pembayaran
MIDTRANS_URL = "https://api.sandbox.midtrans.com/v2/charge"

# Database user membership (sementara pakai dict)
memberships = {}

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Halo! Selamat datang di Membership Bot 🚀\nGunakan /buy untuk membeli akses.")

async def buy(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    amount = 15000  # Harga 15.000 IDR
    
    headers = {
        "Authorization": "Basic " + MIDTRANS_SERVER_KEY,
        "Content-Type": "application/json",
    }
    
    data = {
        "payment_type": "gopay",
        "transaction_details": {
            "order_id": f"ORDER-{user_id}-{int(time.time())
