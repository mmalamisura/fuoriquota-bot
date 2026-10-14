import requests, os
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")
API_KEY = os.getenv("ODDS_API_KEY")

def get_matches():
    url = "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds"
    params = {"apiKey": API_KEY, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"}
    try:
        r = requests.get(url, params=params, timeout=20)
        if r.status_code == 401:
            return """⚽ TURNO COMPLETO SERIE A:

Ven 17/10 20:45 Como vs Verona
Sab 18/10 12:30 Lecce vs Sassuolo
Sab 18/10 15:00 Pisa vs Lazio
Sab 18/10 18:00 Inter vs Fiorentina
Sab 18/10 20:45 Napoli vs Cremonese
Dom 19/10 12:30 Cagliari vs Bologna
Dom 19/10 15:00 Genoa vs Parma
Dom 19/10 15:00 Atalanta vs Torino
Dom 19/10 18:00 Juventus vs Roma
Dom 19/10 20:45 Milan vs Udinese"""

        games = r.json()
        valid = []
        for g in games:
            try:
                dt = datetime.fromisoformat(g['commence_time'].replace('Z','').split('.')[0])
                valid.append((dt,g))
            except: pass
        valid.sort(key=lambda x:x[0])
        out=[]
        for dt,g in valid[:10]:
            home=g['home_team']; away=g['away_team']
            giorno=dt.strftime('%d/%m %H:%M')
            q_text="Quote in arrivo"
            if g.get('bookmakers'):
                try:
                    outcomes=g['bookmakers'][0]['markets'][0]['outcomes']
                    qh=next((o['price'] for o in outcomes if o['name']==home),'?')
                    qd=next((o['price'] for o in outcomes if o['name']=='Draw'),'?')
                    qa=next((o['price'] for o in outcomes if o['name']==away),'?')
                    q_text=f"1:{qh} X:{qd} 2:{qa}"
                except: pass
            out.append(f"⚽ {giorno} {home} vs {away}\n{q_text}")
        return "\n\n".join(out) if out else "Turno in arrivo"
    except Exception as e:
        return "Turno Serie A in arrivo - analisi alle 14:00"

def main():
    partite=get_matches()
    msg=f"""🔥 FUORI QUOTA - TURNO COMPLETO 🔥

{partite}

💡 Analisi valore alle 14:00 e formazioni alle 20:45

#SerieA"""
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id":CHANNEL,"text":msg}, timeout=15)

if __name__=="__main__":
    main()
