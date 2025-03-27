import os
from dotenv import load_dotenv
import midtransclient

# Memuat variabel lingkungan
load_dotenv()

server_key = os.getenv("MIDTRANS_SERVER_KEY")
client_key = os.getenv("MIDTRANS_CLIENT_KEY")

if not server_key or not client_key:
    raise ValueError("MIDTRANS_SERVER_KEY or MIDTRANS_CLIENT_KEY is not set in the environment variables")

# Inisialisasi Midtrans
midtrans = midtransclient.Snap(
    is_production=False,
    server_key=server_key
)

def create_payment_link(user, amount):
    transaction_details = {
        'transaction_details': {
            'order_id': f"order-{user.id}",
            'gross_amount': amount
        },
        'customer_details': {
            'first_name': user.first_name
        }
    }

    try:
        transaction = midtrans.create_transaction(transaction_details)
        return transaction['redirect_url']
    except Exception as e:
        print(f"Error creating payment link: {e}")
        return None
