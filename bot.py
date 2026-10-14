import requests, os
from datetime import datetime, timedelta

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")
API_KEY = os.getenv("ODDS_API_KEY")

def get_matches():
    url = "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds"
    params = {"apiKey": API_KEY, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"}
    try:
        r = requests.get(url, params=params, timeout=20)
        print(f"DEBUG API status: {r.status_code}, eventi: {len(r.json()) if r.status_code==200 else 0}")
        if r.status_code!= 200:
            return f"Quota in aggiornamento (API {r.status_code}). Prossimo scan 20:45."

        games = r.json()
        if not games:
            return "Nessuna quota Serie A disponibile ora (pausa nazionali o mercato chiuso). Prossimo scan alle 20:45 con le quote di domani."

        # Filtro 72h + ordina per data
        now = datetime.utcnow()
        future = now + timedelta(hours=72)
        valid = []
        for g in games:
            try:
                dt = datetime.fromisoformat(g['commence_time'].replace('Z','+00:00'))
                if now - timedelta(hours=2) <= dt <= future:
                    valid.append((dt, g))
            except: pass

        valid.sort(key=lambda x: x[0])

        if not valid:
            # Se nulla nelle 72h, mostra le più vicine in assoluto
            valid = sorted([(datetime.fromisoformat(g['commence_time'].replace('Z','+00:00')), g) for g in games], key=lambda x: x[0])[:3]

        out = []
        for dt, g in valid[:4]:
            home = g['home_team']; away = g['away_team']
            giorno = dt.strftime('%a %d/%m %H:%M')
            q = '?'
            if g.get('bookmakers'):
                try:
                    outcomes = g['bookmakers'][0]['markets'][0]['outcomes']
                    q_home = next((o['price'] for o in outcomes if o['name']==home), '?')
                    q_away = next((o['price'] for o in outcomes if o['name']==away), '?')
                    q_draw = next((o['price'] for o in outcomes if o['name']=='Draw'), '?')
                    q = f"1:{q_home} X:{q_draw} 2:{q_away}"
                except: pass
            out.append(f"⚽ {giorno} - {home} vs {away}\n{q}")

        return "\n\n".join(out)

    except Exception as e:
        return f"Aggiornamento quote in corso... {e}"

def main():
    partite = get_matches()
    msg = f"""🔥 FUORI QUOTA - ANALISI ANTICIPATA 🔥

{partite}

💡 I professionisti scommettono 24-48h prima per prendere il valore. Le quote migliori non sono a ridosso del match.

Prossimo aggiornamento: stasera con formazioni ufficiali.

#SerieA #FuoriQuota"""

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL, "text": msg}
    r = requests.post(url, json=payload, timeout=15)
    print(f"Risposta: {r.text}")

if __name__ == "__main__":
    main()
