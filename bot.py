import requests, os
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")
KEY = os.getenv("ODDS_API_KEY")
print(f"DEBUG Token ok: {bool(TOKEN)}")
print(f"DEBUG Channel: {CHANNEL}")
print(f"DEBUG Odds ok: {bool(KEY)}")
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {"chat_id": CHANNEL, "text": "🚀 TEST FUORI QUOTA - Se leggi questo il bot funziona!"}
print(f"DEBUG invio a {CHANNEL}...")
r = requests.post(url, json=payload, timeout=15)
print(f"DEBUG STATUS: {r.status_code}")
print(f"DEBUG RISPOSTA: {r.text}")
