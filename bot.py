import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

def get_value_bets():
    try:
        url = f"https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h&oddsFormat=decimal"
        data = requests.get(url, timeout=15).json()
        messaggi = []
        for match in data[:5]:
            try:
                home = match.get('home_team','')
                away = match.get('away_team','')
                bookmakers = match.get('bookmakers', [])
                if len(bookmakers) < 3: continue
                quotes = []
                for b in bookmakers:
                    for m in b['markets']:
                        if m['key'] == 'h2h':
                            for o in m['outcomes']:
                                if o['name'] == home:
                                    quotes.append((b['title'], o['price']))
                if len(quotes) < 3: continue
                prices = [p[1] for p in quotes]
                media = sum(prices)/len(prices)
                max_q = max(prices)
                book_max = [q[0] for q in quotes if q[1]==max_q][0]
                if max_q > media * 1.08:
                    msg = f"🔍 FUORI QUOTA RILEVATO\n\n🏟️ {home} - {away}\n📊 {home} vittoria\n💰 Media: {media:.2f}\n🚀 MAX su {book_max}: {max_q:.2f} (+{((max_q/media)-1)*100:.0f}% VALORE)\n\n🤖 Bot automatico. 18+ Gioca responsabilmente."
                    messaggi.append(msg)
            except: continue
        return messaggi[:2]
    except: return []

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHANNEL_ID, "text": text})

if __name__ == "__main__":
    for m in get_value_bets():
        send_to_telegram(m)
