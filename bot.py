import requests, os

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")
KEY = os.getenv("ODDS_API_KEY")

print(f"DEBUG: Token inizia con {TOKEN[:10] if TOKEN else 'VUOTO'}...")
print(f"DEBUG: Channel ID = {CHANNEL}")
print(f"DEBUG: Odds Key presente = {'SI' if KEY else 'NO'}")

def send_debug():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL, "text": "🚀 TEST FUORI QUOTA - Se leggi questo il bot funziona!"}
    print(f"DEBUG: Provo a inviare a {CHANNEL}")
    r = requests.post(url, json=payload, timeout=15)
    print(f"DEBUG RISPOSTA TELEGRAM: Status {r.status_code}")
    print(f"DEBUG RISPOSTA TELEGRAM: {r.text}")

if __name__ == "__main__":
    send_debug()
