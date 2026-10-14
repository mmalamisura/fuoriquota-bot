import requests, os
from datetime import datetime, timedelta

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")
API_KEY = os.getenv("ODDS_API_KEY")

print("DEBUG: Avvio bot 72h")

def get_matches():
    url = "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds"
    params = {"apiKey": API_KEY, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"}
    r = requests.get(url, params=params, timeout=20)
    print(f"DEBUG API status {r.status_code}")
    if r.status_code!= 200:
        print(r.text)
        return f"Quote Serie A in aggiornamento (API {r.status_code})"

    games = r.json()
    print(f"DEBUG trovati {len(games)} eventi")
    if not games:
        return "Pausa Serie A o mercato chiuso. Torniamo domani con il prossimo turno."

    now = datetime.utcnow()
    future = now + timedelta(hours=72)
    valid = []
    for g in games:
        try:
            dt = datetime.fromisoformat(g['commence_time'].replace('Z','+00:00').replace('+00:00','').split('.')[0])
            # prendi tutto, anche se tra 3 giorni
            valid.append((dt, g))
        except Exception as e:
            print(f"Parse error {e}")

    valid.sort(key=lambda x: x[0])
    out = []
    for dt, g in valid[:5]:
        home = g['home_team']
        away = g['away_team']
        giorno = dt.strftime('%d/%m %H:%M')
        q_text = "Quote in arrivo"
        if g.get('bookmakers'):
            try:
                outcomes = g['bookmakers'][0]['markets'][0]['outcomes']
                q_home = next((o['price'] for o in outcomes if o['name']==home), '?')
                q_draw = next((o['price'] for o in outcomes if o['name']=='Draw'), '?')
                q_away = next((o['price'] for o in outcomes if o['name']==away), '?')
                q_text = f"1:{q_home} X:{q_draw} 2:{q_away}"
            except Exception as e:
                print(f"quota error {e}")
        out.append(f"⚽ {giorno} - {home} vs {away}\n{q_text}")

    return "\n\n".join(out) if out else "Nessun match trovato, ma API ok"

def main():
    partite = get_matches()
    msg = f"""🔥 FUORI QUOTA - 72H ANTICIPO 🔥

{partite}

💡 Il valore si prende 24-48h PRIMA. Alle 20:45 le formazioni ufficiali.

Prossimo update automatico alle 14:00 e 20:45.

#SerieA"""
    print(f"DEBUG invio msg lungo {len(msg)}")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL, "text": msg}
    res = requests.post(url, json=payload, timeout=15)
    print(f"DEBUG Telegram {res.status_code} {res.text}")

if __name__ == "__main__":
    main()
