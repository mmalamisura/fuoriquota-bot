import requests, os
from datetime import datetime, timedelta

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")
API_KEY = os.getenv("ODDS_API_KEY")

def get_next_update():
    now = datetime.utcnow() + timedelta(hours=2)
    h = now.hour
    if h < 9: return "Oggi alle 09:00"
    if h < 14: return "Oggi alle 14:00"
    if h < 20: return "Oggi alle 20:45"
    return "Domani alle 09:00"

def get_matches():
    url = "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds"
    params = {"apiKey": API_KEY, "regions": "eu", "markets": "h2h,totals,btts", "oddsFormat": "decimal"}

    giorni_en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    giorni_it = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

    try:
        r = requests.get(url, params=params, timeout=20)
        print(f"API status {r.status_code}")
        if r.status_code!= 200:
            # Se API down, prova solo h2h
            params["markets"] = "h2h"
            r = requests.get(url, params=params, timeout=20)
            if r.status_code!= 200:
                return None

        games = r.json()
        if not games:
            return None

        out = []
        for g in games[:4]:
            try:
                dt = datetime.fromisoformat(g['commence_time'].replace('Z','+00:00'))
                en = dt.strftime('%a')
                it = giorni_it[giorni_en.index(en)] if en in giorni_en else en
                data = f"{it} {dt.strftime('%d/%m %H:%M')}"

                home = g['home_team']
                away = g['away_team']

                q1 = qx = q2 = "?"
                gol = over = "?"

                if g.get('bookmakers'):
                    bm = g['bookmakers'][0]
                    for m in bm.get('markets', []):
                        if m['key'] == 'h2h':
                            for o in m['outcomes']:
                                if o['name'] == home: q1 = o['price']
                                elif o['name'] == 'Draw': qx = o['price']
                                elif o['name'] == away: q2 = o['price']
                        if m['key'] == 'btts':
                            for o in m['outcomes']:
                                if o['name'] == 'Yes': gol = o['price']
                        if m['key'] == 'totals':
                            for o in m['outcomes']:
                                if o['name'] == 'Over' and str(o.get('point')) == '2.5': over = o['price']

                # ANALISI FUORI QUOTA - SEMPRE, anche se manca qualche quota
                analisi = ""
                try:
                    if gol!= "?" and float(gol) <= 1.80:
                        analisi = f"🔥 FUORI QUOTA: GOL a {gol} -> entrambe segnano, book ancora alto"
                    elif over!= "?" and float(over) >= 1.95:
                        analisi = f"🔥 FUORI QUOTA: OVER 2.5 a {over} -> attacco vs difesa, valore"
                    elif q1!= "?" and float(q1) >= 2.30:
                        analisi = f"👀 Valore su 1 a {q1} -> casa favorita ma quota alta"
                    else:
                        analisi = f"Quota da monitorare, analisi completa alle 14:00 con infortuni"
                except:
                    analisi = f"Analisi completa alle 14:00 con infortuni"

                out.append(
                    f"⚽ {data} - {home} vs {away}\n"
                    f"1={q1} | X={qx} | 2={q2} | GOL={gol} | OVER={over}\n"
                    f"{analisi}"
                )
            except Exception as e:
                print(f"Errore partita {e}")
                continue

        return "\n\n".join(out) if out else None

    except Exception as e:
        print(f"Errore generale {e}")
        return None

def main():
    partite = get_matches()
    next_up = get_next_update()

    # Se API proprio non va, mostra messaggio con mission del canale
    if not partite:
        partite = (
            "⚽ Ven 17/10 20:45 - Quote Serie A in aggiornamento\n"
            "1=? X=? 2=? | GOL=? OVER=?\n"
            "🔥 Analisi fuori quota in arrivo alle 20:45 con formazioni"
        )

    msg = f"""🎯 FUORI QUOTA

Non ti diamo pronostici. Ti diciamo dove il bookmaker ha sbagliato la quota.

{partite}

━━━━━━━━━━━━━━━
📌 Come leggiamo: Se GOL è a 1.75 ma entrambe segnano da 5 partite, è fuori quota.
Non giochiamo chi vince, giochiamo l'errore del book.

⏰ 3 aggiornamenti automatici: 09:00 / 14:00 / 20:45
Prossimo: {next_up}

#SerieA #FuoriQuota"""

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL, "text": msg}
    res = requests.post(url, json=payload, timeout=15)
    print(f"Telegram {res.status_code}")

if __name__ == "__main__":
    main()
    main()
