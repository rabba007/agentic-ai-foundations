import requests
import os
def send_message(message, parse_mode=None):
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    CHAT_ID = os.getenv('TELEGRAM_BOT_CHAT_ID')
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    r = requests.post(url, data=payload)
    if r.status_code == 200:
        print("📩 Message sent successfully!")
    else:
        print("❌ Failed to send message:", r.text)