import requests
import os

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = "https://tele-bot-production-8c1a.up.railway.app/" + TELEGRAM_BOT_TOKEN

response = requests.post(
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook",
    data={"url": WEBHOOK_URL}
)

print(response.text)

