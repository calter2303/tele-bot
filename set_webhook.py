import requests
import os

WEBHOOK_URL = "https://tele-bot-production-8c1a.up.railway.app/" + os.getenv("TELEGRAM_BOT_TOKEN")  # Ganti dengan URL dari Railway

response = requests.post(
    f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/setWebhook",
    data={"url": WEBHOOK_URL}
)

print(response.text)
