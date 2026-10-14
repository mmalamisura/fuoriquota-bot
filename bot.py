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

def analyze_match(home, away, q1, qx, q2, gol, over):
    """Qui sta il FUORI QUOTA"""
    analisi = []

    # Converti in float se possibile
    try:
        q1_f = float(q1)
        q2_f = float(q2)
        gol_f = float(gol)
        over_f = float(over)
    except:
        return "Analisi in arrivo alle 14:00 con formazioni"

    # LOGICA FUORI QUOTA SEMPLICE MA EFFICACE
    if over_f >= 2.00:
        analisi.append(f"🔥 OVER 2.5 a {over} FUORI QUOTA -> 2 squadre offensive, book lo da alto")
    elif over_f <= 1.60:
        analisi.append(f"🔥 UNDER 2.5 a {over} probabile -> difese solide")

    if gol_f!= "?" and gol_f <= 1.75:
        analisi.append(f"🔥 GOL a {gol} FUORI QUOTA -> entrambe segnano tanto, quota ancora giocabile")

    if q1_f >= 2.2 and q1_f <= 2.8:
        analisi.append(f"👀 1 a {q1} interessante -> casa favorita ma quota alta")

    if not analisi:
        analisi.append(f"Quota equilibrata, aspettiamo news formazioni")

    return "\n".join(analisi)

def get_matches():
    url = "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds"
    params = {"apiKey": API_KEY, "regions": "eu", "markets": "h2h,totals,btts", "oddsFormat": "decimal"}
    try:
        r = requests.get(url, params=params, timeout=20)
        if r.status_code!=200: return None
        games = r.json()

        giorni_en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        giorni_it = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

        out = []
        for g in games[:3]: # SOLO 3 PARTITE ANALIZZATE A FONDO, non 8
            try:
                dt = datetime.fromisoformat(g['commence_time'].replace('Z','+00:00'))
                it_day = giorni_it[giorni_en.index(dt.strftime('%a'))]
                data = f"{it_day} {dt.strftime('%d/%m %H:%M')}"

                home = g['home_team']; away = g['away_team']
                q1=q2=qx=gol=over="?"

                if g.get('bookmakers'):
                    for m in g['bookmakers'][0].get('markets',[]):
                        if m['key']=='h2h':
                            for o in m['outcomes']:
                                if o['name']==home: q1=o['price']
                                elif o['name']=='Draw': qx=o['price']
                                elif o['name']==away: q2=o['price']
                        if m['key']=='btts':
                            for o in m['outcomes']:
                                if o['name']=='Yes': gol=o['price']
                        if m['key']=='totals':
                            for o in m['outcomes']:
                                if o['name']=='Over' and o.get('point')==2.5: over=o['price']

                analisi = analyze_match(home, away, q1, qx, q2, gol, over)

                out.append(
                    f"⚽ {data} - {home} vs {away}\n"
                    f"Quote: 1={q1} X={qx} 2={q2} | GOL={gol} OVER={over}\n"
                    f"{analisi}"
                )
            except Exception as e:
                print(e)
                continue
        return "\n\n---\n\n".join(out)
    except:
        return None

def main():
    partite = get_matches()
    next_up = get_next_update()

    if not partite:
        partite = "Analisi in aggiornamento, torniamo a breve."

    msg = f"""🎯 FUORI QUOTA - Dove il bookmaker sbaglia

{partite}

━━━━━━━━━━━━━━━
📌 Come leggiamo: Se OVER è a 2.10 ma le squadre segnano tanto, è FUORI QUOTA.
Non giochiamo la favorita, giochiamo l'errore.

⏰ Prossimo aggiornamento: {next_up}
Alle 14:00 analisi con infortuni, alle 20:45 con formazioni ufficiali.

#FuoriQuota"""

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHANNEL, "text": msg}, timeout=15)

if __name__ == "__main__":
    main()
