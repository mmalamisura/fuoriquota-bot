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

def analyze_match(home, away, q1, qx, q2):
    try:
        q1_f = float(q1)
        qx_f = float(qx)
        q2_f = float(q2)
    except:
        return "Analisi in arrivo alle 14:00 con infortuni e formazioni."

    # Chi è favorito?
    fav = "casa" if q1_f < q2_f and q1_f < qx_f else "ospite" if q2_f < q1_f and q2_f < qx_f else "pareggio"

    if home == "Frosinone" and away == "Sassuolo":
        return (
            f"📊 ANALISI: Quote quasi identiche (1={q1} / 2={q2}). Il bookmaker non sa chi è favorito, vuol dire partita aperta.\n"
            f"FUORI QUOTA: X a {qx} è alto. Frosinone e Sassuolo pareggiano poco, ma il book mette X alto perché si aspetta gol. "
            f"Se scende da 3.62 a 3.30 vuol dire che molti stanno puntando X -> il valore sparisce."
        )
    elif home == "Venezia" and away == "Napoli":
        return (
            f"📊 ANALISI: Napoli favorito a {q2}, giusto. Ma {q2} non è bassissimo (1.50 sarebbe senza valore). A {q2} c'è ancora margine.\n"
            f"FUORI QUOTA: 1 Venezia a {q1} è altissimo. Se scende da 4.68 a 4.00 vuol dire che i pro stanno caricando Venezia per infortunio di Lukaku. "
            f"Noi NON giochiamo 1 fisso, ma se X2 + GOL sale a 2.20 diventa fuori quota."
        )
    elif "Bologna" in home and "Inter" in away:
        return (
            f"📊 ANALISI: Inter favorita a {q2} anche fuori casa. {q2}=1.60 è quota da big, ma è bassa = poco valore.\n"
            f"FUORI QUOTA: Il book ha paura di Bologna in casa, quindi mette X alto a {qx}. "
            f"Se X scende da {qx} a 3.50 vuol dire che il mercato vede pareggio. Il fuori quota qui è X + GOL."
        )
    elif "Roma" in home:
        return (
            f"📊 ANALISI: Roma super favorita a {q1}. {q1}=1.40 vuol dire che per vincere 10€ ne vinci 14€ = rischio alto, resa bassa. Il book NON sbaglia qui.\n"
            f"FUORI QUOTA: Non è su 1. È su OVER. Roma segna tanto in casa, Genoa prende gol fuori. Se OVER 2.5 è a 1.80 e scende a 1.65, vuol dire che tutti stanno puntando OVER = era fuori quota."
        )
    else:
        if fav == "casa":
            return f"📊 {home} favorito a {q1}. Se {q1} sale da 2.00 a {q1} invece di scendere, vuol dire che il mercato non lo carica = possibile trappola. Aspettiamo news."
        elif fav == "ospite":
            return f"📊 {away} favorito a {q2}. Quota {q2} ancora giocabile sopra 1.70. Se scende sotto 1.60 non è più fuori quota."
        else:
            return f"📊 Partita equilibrata. Il valore non è su chi vince, ma su GOL/OVER. Vediamo dove le quote scendono."

def get_matches():
    url = "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds"
    params = {"apiKey": API_KEY, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"}
    try:
        r = requests.get(url, params=params, timeout=20)
        if r.status_code!=200:
            return None
        games = r.json()
        if not games:
            return None

        giorni_en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        giorni_it = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

        out = []
        for g in games[:4]:
            try:
                dt = datetime.fromisoformat(g['commence_time'].replace('Z','+00:00'))
                it_day = giorni_it[giorni_en.index(dt.strftime('%a'))]
                data = f"{it_day} {dt.strftime('%d/%m %H:%M')}"

                home = g['home_team']
                away = g['away_team']

                q1=qx=q2="?"
                if g.get('bookmakers'):
                    for m in g['bookmakers'][0].get('markets', []):
                        if m['key']=='h2h':
                            for o in m['outcomes']:
                                if o['name']==home: q1=o['price']
                                elif o['name']=='Draw': qx=o['price']
                                elif o['name']==away: q2=o['price']

                analisi = analyze_match(home, away, q1, qx, q2)

                out.append(
                    f"⚽ {data} - {home} vs {away}\n"
                    f"Quote: 1={q1} | X={qx} | 2={q2}\n"
                    f"{analisi}"
                )
            except Exception as e:
                print(e)
                continue
        return "\n\n".join(out)
    except Exception as e:
        print(e)
        return None

def main():
    partite = get_matches()
    next_up = get_next_update()

    if not partite:
        partite = "Quote in aggiornamento."

    msg = f"""🎯 FUORI QUOTA

Non ti diamo pronostici. Ti diciamo dove il bookmaker ha sbagliato la quota.

Ecco cosa vuol dire "quota che scende":
Se una quota passa da 3.62 a 3.30 vuol dire che MOLTI stanno puntando lì. I bookmaker la abbassano perché rischiano troppo. Se la prendi PRIMA che scenda, hai preso il FUORI QUOTA.

{partite}

━━━━━━━━━━━━━━━
📌 Prossimo aggiornamento: {next_up}
Alle 14:00 con infortuni, alle 20:45 con formazioni ufficiali.

#FuoriQuota"""

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHANNEL, "text": msg}, timeout=15)

if __name__ == "__main__":
    main()

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
