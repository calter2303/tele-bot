import os
import logging
import asyncio
from flask import Flask
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import uvicorn
from membership import add_member, is_member, remove_member  # Import fungsi dari membership.py

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

# Menambahkan handler baru untuk perintah add, check, remove
application.add_handler(CommandHandler("add", add))
application.add_handler(CommandHandler("check", check_member))
application.add_handler(CommandHandler("remove", remove))

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

async def run_flask():
    """Menjalankan Flask dengan Uvicorn di Railway."""
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    """Jalankan Telegram bot & Flask secara bersamaan."""
    task1 = asyncio.create_task(run_telegram())
    task2 = asyncio.create_task(run_flask())
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    asyncio.run(main())  # 🔥 GUNAKAN `asyncio.run(main())` AGAR LOOP DIKELOLA DENGAN BENAR
