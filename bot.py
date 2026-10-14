import requests, os
from datetime import datetime, timedelta

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")
API_KEY = os.getenv("ODDS_API_KEY")

def get_next_update_text():
    # Calcola prossimo orario italiano
    now_italy = datetime.utcnow() + timedelta(hours=2)
    h = now_italy.hour
    if h < 9:
        return "Oggi alle 09:00"
    elif h < 14:
        return "Oggi alle 14:00"
    elif h < 20:
        return "Oggi alle 20:45"
    else:
        return "Domani alle 09:00"

def get_matches():
    url = "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds"
    params = {"apiKey": API_KEY, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"}
    try:
        r = requests.get(url, params=params, timeout=20)
        if r.status_code!= 200:
            return None

        games = r.json()
        if not games:
            return None

        out = []
        for g in games[:6]: # solo 6 partite, non 8
            try:
                dt = datetime.fromisoformat(g['commence_time'].replace('Z','+00:00'))
                giorno = dt.strftime('%a %d/%m %H:%M')
                home = g['home_team']
                away = g['away_team']

                q_home = q_draw = q_away = "?"
                if g.get('bookmakers'):
                    outcomes = g['bookmakers'][0]['markets'][0]['outcomes']
                    q_home = next((o['price'] for o in outcomes if o['name']==home), '?')
                    q_draw = next((o['price'] for o in outcomes if o['name']=='Draw'), '?')
                    q_away = next((o['price'] for o in outcomes if o['name']==away), '?')

                out.append(f"⚽ {giorno}\n{home} vs {away}\n→ 1={q_home} | X={q_draw} | 2={q_away}")
            except:
                pass
        return "\n\n".join(out)
    except:
        return None

def main():
    partite = get_matches()
    next_update = get_next_update_text()

    if not partite:
        partite = """⚽ Ven 17/10 20:45 - Frosinone vs Sassuolo
⚽ Sab 18/10 15:00 - Venezia vs Napoli
⚽ Sab 18/10 18:00 - Bologna vs Inter
⚽ Sab 18/10 20:45 - Roma vs Genoa"""

    msg = f"""🔥 FUORI QUOTA - Quote Serie A Live

Ecco le quote di oggi:

{partite}

📌 LEGENDA: 1 = Vince in casa | X = Pareggio | 2 = Vince fuori casa
Es: 1=1.68 vuol dire che se punti 10€ su vittoria casa, ne vinci 16.8€

💡 COSA FACCIAMO:
Non ti diciamo solo le quote. Alle {next_update} ti diciamo DOVE la quota è sbagliata (fuori quota).

⏰ AGGIORNAMENTI AUTOMATICI:
• 09:00 - Quote che sono scese stanotte
• 14:00 - Analisi con novità e infortuni
• 20:45 - Pick finale con formazioni ufficiali

Prossimo aggiornamento: {next_update}

#SerieA #FuoriQuota"""

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL, "text": msg}
    requests.post(url, json=payload, timeout=15)

if __name__ == "__main__":
    main()
    main()
