import os
import logging
import asyncio
from flask import Flask
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler, State
import uvicorn
from membership_db import add_member, is_member, remove_member, create_db  # Import fungsi dari membership_db.py
from payment_service import create_payment_link  # Fungsi pembayaran (misalnya menggunakan Midtrans)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = int(os.getenv("PORT", 8000))  # Railway pakai env PORT

# Setup logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Setup Flask
app = Flask(__name__)

# Setup Telegram bot
application = Application.builder().token(TOKEN).build()

# Menentukan state untuk percakapan
EMAIL = 1  # State untuk meminta email

# Variabel penyimpanan sementara untuk email
user_email = {}

# Fungsi untuk meminta email
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! To proceed with the payment, I need your email address. Please provide it.")

    # Mengubah state ke EMAIL
    return EMAIL

# Fungsi untuk menangani input email
async def handle_email(update: Update, context: CallbackContext):
    email = update.message.text  # Ambil email yang diberikan oleh pengguna
    user_id = update.message.from_user.id
    
    # Simpan email di penyimpanan sementara atau database
    user_email[user_id] = email
    
    # Informasikan pengguna bahwa email sudah diterima
    await update.message.reply_text(f"Thank you! We have received your email: {email}. Now we will proceed with your payment.")
    
    # Lanjutkan ke proses pembayaran
    payment_link = create_payment_link(update.message.from_user, 1000)  # 1000 adalah jumlah dalam satuan terkecil (misalnya 1000 untuk 10.00 IDR)
    
    if payment_link:
        await update.message.reply_text(f"Please complete your payment using this link: {payment_link}")
    else:
        await update.message.reply_text("There was an error creating the payment link. Please try again later.")
    
    return ConversationHandler.END  # Akhiri percakapan setelah email diberikan dan pembayaran diproses

# Fungsi untuk membatalkan percakapan
async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Payment process has been canceled.")
    return ConversationHandler.END  # Mengakhiri percakapan jika dibatalkan

# Menambahkan handler percakapan untuk meminta email
conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("pay", start)],  # Menggunakan perintah /pay untuk memulai percakapan
    states={
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email)]  # Mendengarkan input email pengguna
    },
    fallbacks=[CommandHandler("cancel", cancel)]  # Menyediakan opsi untuk membatalkan percakapan
)

# Fungsi untuk memberikan link kepada pengguna
async def join(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    
    # Mengecek apakah pengguna sudah menjadi member atau belum
    if is_member(user_id):
        await update.message.reply_text(f"Hello {username}, you are already a member!")
    else:
        # Jika belum menjadi member, kirimkan link untuk bergabung
        invite_link = "https://t.me/+u_XdTxJT_LgzYjE1"  # Gantilah dengan link undanganmu
        await update.message.reply_text(f"Hello {username}, you can join the membership by using this link: {invite_link}")

# Fungsi untuk menambahkan anggota
async def add(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    add_member(user_id, username)
    await update.message.reply_text(f"Hello {username}, you have been added as a member!")

# Fungsi untuk mengecek apakah anggota sudah terdaftar
async def check_member(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if is_member(user_id):
        await update.message.reply_text("You are already a member!")
    else:
        await update.message.reply_text("You are not a member yet.")

# Fungsi untuk menghapus anggota
async def remove(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    remove_member(user_id)
    await update.message.reply_text("You have been removed from membership.")

# Fungsi start dan echo
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Bot is running!")

async def echo(update: Update, context: CallbackContext):
    await update.message.reply_text(update.message.text)

# Tambahkan handler
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Menambahkan handler baru untuk perintah add, check, remove, dan join
application.add_handler(CommandHandler("add", add))
application.add_handler(CommandHandler("check", check_member))
application.add_handler(CommandHandler("remove", remove))
application.add_handler(CommandHandler("join", join))  # Handler untuk /join

# Menambahkan handler percakapan untuk meminta email dan pembayaran
application.add_handler(conversation_handler)

@app.route("/")
def index():
    return "Bot is alive!"

async def run_telegram():
    """Menjalankan bot Telegram tanpa menutup event loop."""
    await application.initialize()
    await application.start()
    await application.updater.start_polling()  # 🔥 GUNAKAN `start_polling()`, BUKAN `run_polling()`
    logging.info("Telegram bot started!")
    while True:
        await asyncio.sleep(1)  # 🔥 Pastikan loop tetap berjalan

# Fungsi untuk menjalankan Flask dengan Uvicorn
def run_flask():
    """Menjalankan Flask dengan Uvicorn di Railway."""
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="info")
    server = uvicorn.Server(config)
    server.run()

async def main():
    """Jalankan Telegram bot & Flask secara bersamaan."""
    task1 = asyncio.create_task(run_telegram())  # Menjalankan Telegram bot
    task2 = asyncio.to_thread(run_flask)  # Menjalankan Flask di thread terpisah
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    # Membuat database dan tabel jika belum ada
    create_db()
    
    asyncio.run(main())  # Menjalankan event loop
