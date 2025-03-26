from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from payment_service import create_payment_link  # Pastikan modul ini ada dan fungsinya benar
from membership_db import is_member  # Pastikan modul ini ada dan fungsinya benar

# Menentukan state untuk percakapan
EMAIL = 1  # State untuk meminta email

# Variabel penyimpanan sementara untuk email
user_email = {}

# Fungsi untuk memulai percakapan
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! To proceed with the payment, I need your email address. Please provide it.")

    # Mengubah state ke EMAIL
    return EMAIL

# Fungsi untuk menangani email
async def handle_email(update: Update, context: CallbackContext):
    email = update.message.text  # Ambil email yang diberikan oleh pengguna
    user_id = update.message.from_user.id
    
    # Simpan email di penyimpanan sementara
    user_email[user_id] = email
    
    # Cek apakah pengguna sudah terdaftar dan sudah membayar
    if is_member(user_id):
        await update.message.reply_text("You are already a member and your payment is confirmed!")
        return ConversationHandler.END

    # Informasikan pengguna bahwa email sudah diterima
    await update.message.reply_text(f"Thank you! We have received your email: {email}. Now we will proceed with your payment.")
    
    # Lanjutkan ke proses pembayaran (atau lakukan hal lain yang diperlukan)
    payment_link = create_payment_link(update.message.from_user, 1000, email)  # 1000 adalah jumlah dalam satuan terkecil (misalnya 1000 untuk 10.00 IDR)
    
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

# Setup bot dengan handler percakapan
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()  # Menggunakan variabel TELEGRAM_BOT_TOKEN
application.add_handler(conversation_handler)
application.run_polling()
