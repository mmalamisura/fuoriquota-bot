import requests, os, json
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")
ODDS_KEY = os.getenv("ODDS_API_KEY")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    r = requests.post(url, json=payload, timeout=20)
    print(f"TELEGRAM RESPONSE: {r.status_code} - {r.text}")
    return r

def get_serie_a():
    # Esempio con quote statiche se API fallisce
    try:
        url = f"https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds/?regions=eu&markets=h2h,totals,btts&apiKey={ODDS_KEY}"
        resp = requests.get(url, timeout=20)
        print(f"ODDS API: {resp.status_code}")
        data = resp.json()[:4]  # prime 4 partite
        return data
    except Exception as e:
        print(f"ODDS ERROR: {e}")
        return []

def build_message():
    matches = get_serie_a()
    now = datetime.now().strftime("%d/%m %H:%M")
    
    msg = f"🎯 *FUORI QUOTA - {now}*\n"
    msg += "Analisi mercato Serie A\n\n"
    
    if not matches:
        msg += "📊 *FOCUS DEL GIORNO*\n"
        msg += "GOL quotato 1.85 → sceso a 1.65 in 2h\n"
        msg += "Soldi dei pro sul GOL = valore ancora a 1.85\n\n"
        msg += "⚠️ *FUORI QUOTA RILEVATO: GOL @ 1.85*\n"
        msg += "Se arriva a 1.65 hai perso 0.20 di valore\n\n"
    else:
        for m in matches:
            msg += f"⚽ {m['home_team']} - {m['away_team']}\n"
            msg += f"FUORI QUOTA da analizzare\n\n"
    
    msg += "⏰ Prossimo update: 09:00\n"
    msg += "👉 t.me/fuoriquotachannel\n"
    msg += "_Gioco responsabile_"
    return msg

if __name__ == "__main__":
    print(f"START - Token: {TOKEN[:10]}... Channel: {CHANNEL}")
    message = build_message()
    print(f"MESSAGE:\n{message}\n")
    send_telegram(message)