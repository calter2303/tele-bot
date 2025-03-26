import os
import midtransclient
from dotenv import load_dotenv
from membership_db import update_payment_status

# Muat .env file
load_dotenv()

# Ambil server_key dan client_key dari environment variables
server_key = os.getenv("MIDTRANS_SERVER_KEY")
client_key = os.getenv("MIDTRANS_CLIENT_KEY")

# Pastikan key tersebut ada
if not server_key or not client_key:
    raise ValueError("MIDTRANS_SERVER_KEY or MIDTRANS_CLIENT_KEY is not set in the environment variables")

# Inisialisasi Midtrans
midtrans = midtransclient.CoreApi(
    is_production=False,  # Set ke True jika di lingkungan produksi
    server_key=server_key,  # Gantilah dengan server key dari Midtrans
    client_key=client_key   # Gantilah dengan client key dari Midtrans
)

def create_payment_link(user, amount, email):
    # Data transaksi yang diperlukan oleh Midtrans
    transaction_details = {
        'order_id': f"order-{user['id']}",  # Gantilah dengan ID pesanan unik
        'gross_amount': amount  # Jumlah yang harus dibayar
    }

    # Metadata pengguna dari Telegram
    customer_details = {
        'first_name': user['first_name'],  # Nama depan pengguna
        'email': email,  # Email yang diterima sebagai parameter
    }

    # Membuat transaksi menggunakan Midtrans
    try:
        transaction = midtrans.transaction.create(transaction_details, customer_details)
        payment_url = transaction['redirect_url']
        payment_id = transaction['transaction_id']  # ID pembayaran yang dihasilkan oleh Midtrans
        
        # Update status pembayaran ke database
        update_payment_status(user['id'], payment_id)

        return payment_url
    except Exception as e:
        print(f"Error creating payment link: {e}")
        return None
