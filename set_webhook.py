import requests

# Ganti dengan URL webhook dari aplikasi Railway kamu
WEBHOOK_URL = "https://tele-bot-production-8c1a.up.railway.app/7654581013:AAFcKVBMI5631hzxLdI8myDrw_1BISLISH0"

# Ganti <your-telegram-bot-token> dengan token bot Telegram kamu
response = requests.post(
    f"https://api.telegram.org/bot<your-telegram-bot-token>/setWebhook",
    data={"url": WEBHOOK_URL}
)

print(response.text)
