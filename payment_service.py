# Misalnya, menggunakan Stripe sebagai contoh layanan pembayaran

import stripe

# Inisialisasi Stripe
stripe.api_key = "YOUR_STRIPE_SECRET_KEY"  # Gantilah dengan Secret Key dari Stripe

def create_payment_link(user_id, amount):
    # Membuat Payment Intent di Stripe
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency="usd",  # Gantilah dengan mata uang yang sesuai
        metadata={'user_id': user_id}
    )
    # Kembalikan client secret atau link pembayaran untuk frontend
    return intent.client_secret

def verify_payment_status(payment_id):
    # Memverifikasi status pembayaran
    payment = stripe.PaymentIntent.retrieve(payment_id)
    if payment.status == "succeeded":
        return True
    return False
