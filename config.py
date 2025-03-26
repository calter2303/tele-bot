import os
from dotenv import load_dotenv
import midtransclient

# Muat variabel lingkungan dari .env (hanya diperlukan jika Anda menggunakan file .env di pengembangan lokal)
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
