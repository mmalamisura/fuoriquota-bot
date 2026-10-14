import requests, os
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")
API_KEY = os.getenv("ODDS_API_KEY")

ANALISI = {
    "Como": "VALORE: GOL a 1.80",
    "Lecce": "VALORE: X2 a 1.55",
    "Pisa": "VALORE: Lazio -0.5 a 1.95",
    "Inter": "VALORE: GOL a 1.70",
    "Napoli": "FUORI QUOTA: Napoli -1.5 a 2.10",
    "Cagliari": "VALORE: Under 2.5",
    "Genoa": "VALORE: 1X a 1.35",
    "Juventus": "BIG MATCH: Under 2.5"
}

def main():
    url = "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds"
    params = {"apiKey": API_KEY, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"}
    try:
        r = requests.get(url, params=params, timeout=20)
        games = r.json()
        msg = "🔥 FUORI QUOTA - QUOTE LIVE 🔥\n\n"
        for g in games[:8]:
            home=g['home_team']
            # trova analisi
            analisi = next((v for k,v in ANALISI.items() if k in home), "Analisi alle 14:00")
            # quote live
            q_text=""
            if g.get('bookmakers'):
                try:
                    o=g['bookmakers'][0]['markets'][0]['outcomes']
                    qh=next((x['price'] for x in o if x['name']==home),'?')
                    qd=next((x['price'] for x in o if x['name']=='Draw'),'?')
                    away=g['away_team']
                    qa=next((x['price'] for x in o if x['name']==away),'?')
                    q_text=f"1:{qh} X:{qd} 2:{qa}"
                except: q_text="Quote in agg."
            msg += f"⚽ {home} vs {g['away_team']}\n💡 {q_text} | {analisi}\n\n"
    except:
        msg = "🔥 FUORI QUOTA - TURNO SERIE A 🔥\n\nTurno in arrivo - analisi alle 14:00"

    msg += "\n⏰ 3 UPDATE AL GIORNO"
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id":CHANNEL,"text":msg}, timeout=15)

if __name__=="__main__":
    main()
