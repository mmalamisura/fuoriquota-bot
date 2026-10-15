import requests, os
from datetime import datetime
from zoneinfo import ZoneInfo

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")
ODDS_KEY = os.getenv("ODDS_API_KEY")
ITALY = ZoneInfo("Europe/Rome")
GIORNI_IT = {"Mon":"Lun","Tue":"Mar","Wed":"Mer","Thu":"Gio","Fri":"Ven","Sat":"Sab","Sun":"Dom"}

# SOLO BOOK ADM ITALIANI - APPROVATI PER AFFILIAZIONE
BOOK_ADM_ITALIA = [
    "Bet365", "【entity-Betano¦canonical_name=Betano】", "Bwin", "William Hill", "Betfair",
    "Unibet", "888sport", "Betsson", "LeoVegas", "Goldbet", "Snai"
]

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHANNEL, "text": text, "parse_mode": "Markdown"}, timeout=20)
    return r

def get_from_odds():
    url = "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds/"
    params = {"regions": "eu,uk", "markets": "h2h,totals", "oddsFormat": "decimal", "apiKey": ODDS_KEY}
    resp = requests.get(url, params=params, timeout=20)
    return resp.json() if resp.status_code==200 else []

def build_message():
    now_it = datetime.now(ITALY)
    now_str = now_it.strftime("%d/%m %H:%M")
    odds = get_from_odds()
    odds_sorted = sorted(odds, key=lambda x: x.get('commence_time',''))

    msg = f"🎯 *FUORI QUOTA - {now_str} (IT)*\n"
    msg += f"Serie A - Solo quote ADM Italia - Dove trovare il valore:\n\n"

    giorno_corrente = ""
    for m in odds_sorted:
        home_raw = m['home_team']
        away_raw = m['away_team']
        home = home_raw.replace('Inter Milan','Inter').replace('AC Milan','Milan').replace('Atalanta BC','Atalanta').replace('AS Roma','Roma')
        away = away_raw.replace('Inter Milan','Inter').replace('AC Milan','Milan').replace('Atalanta BC','Atalanta').replace('AS Roma','Roma')

        try:
            dt = datetime.fromisoformat(m['commence_time'].replace('Z','+00:00')).astimezone(ITALY)
            giorno_it = GIORNI_IT.get(dt.strftime("%a"), dt.strftime("%a"))
            giorno_label = dt.strftime("%d/%m")
            ora = dt.strftime("%H:%M")
        except:
            continue

        if giorno_label!= giorno_corrente:
            msg += f"📅 *{giorno_it} {giorno_label}*\n"
            giorno_corrente = giorno_label

        # FILTRO ADM
        book_adm = [b for b in m.get('bookmakers',[]) if any(adm.lower() in b.get('title','').lower() for adm in BOOK_ADM_ITALIA)]
        if not book_adm:
            continue

        h2h_prices = {}
        h2h_book = {}
        for b in book_adm:
            bname = b.get('title','Book')
            for mk in b.get('markets',[]):
                if mk['key']=='h2h':
                    for o in mk['outcomes']:
                        h2h_prices.setdefault(o['name'], []).append(o['price'])
                        if o['name'] not in h2h_book or o['price'] > h2h_book[o['name']][0]:
                            h2h_book[o['name']] = (o['price'], bname)

        best_diff = 0
        best_name = ""; best_price = 0; best_avg = 0
        for name, prices in h2h_prices.items():
            if len(prices) >= 2:
                avg = sum(prices)/len(prices)
                best = max(prices)
                diff = best - avg
                if diff > best_diff:
                    best_diff = diff; best_name = name; best_price = best; best_avg = avg

        q1 = qx = q2 = ""
        main_book = book_adm[0]
        for mk in main_book.get('markets',[]):
            if mk['key']=='h2h':
                for o in mk['outcomes']:
                    if o['name'] == home_raw: q1 = f"1 @{o['price']:.2f}"
                    elif o['name'] == away_raw: q2 = f"2 @{o['price']:.2f}"
                    elif "Draw" in o['name']: qx = f"X @{o['price']:.2f}"

        msg += f"⚽ *{home} - {away}* - {ora}\n"
        msg += f"Quote ADM: {q1} | {qx} | {q2}\n"

        if best_diff >= 0.10:
            perc = (best_diff / best_avg * 100) if best_avg else 0
            dove = h2h_book.get(best_name, (best_price, "Book"))[1]
            # QUI METTERAI IL TUO LINK AFFILIATO
            # Esempio: Betano -> https://www.betano.it/?btag=TUO_CODICE
            if "Draw" in best_name:
                msg += f"💎 FUORI QUOTA: X @{best_price:.2f} su {dove} (media @{best_avg:.2f}) +{perc:.0f}% - Link in bio\n"
            elif best_name == home_raw:
                msg += f"💎 FUORI QUOTA: 1 {home} @{best_price:.2f} su {dove} (media @{best_avg:.2f}) +{perc:.0f}% - Link in bio\n"
            else:
                msg += f"💎 FUORI QUOTA: 2 {away} @{best_price:.2f} su {dove} (media @{best_avg:.2f}) +{perc:.0f}% - Link in bio\n"
        msg += f"\n"

        if len(msg) > 3700:
            break

    msg += f"\n+18 | Gioco responsabile | Solo quote ADM Italia\n"
    msg += f"Info statistiche, non invito a scommettere"
    return msg

if __name__ == "__main__":
    txt = build_message()
    send_telegram(txt)
