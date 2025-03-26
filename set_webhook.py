import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Memuat variabel environment

WEBHOOK_URL = f"https://tele-bot-production-8c1a.up.railway.app/{os.getenv('TELEGRAM_BOT_TOKEN')}"

response = requests.post(
    f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/setWebhook",
    data={"url": WEBHOOK_URL}
)

print(response.text)
