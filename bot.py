import requests, os
from datetime import datetime
from zoneinfo import ZoneInfo

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")
ODDS_KEY = os.getenv("ODDS_API_KEY")
ITALY = ZoneInfo("Europe/Rome")
GIORNI_IT = {"Mon":"Lun","Tue":"Mar","Wed":"Mer","Thu":"Gio","Fri":"Ven","Sat":"Sab","Sun":"Dom"}

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHANNEL, "text": text, "parse_mode": "Markdown"}, timeout=20)
    print(f"TG {r.status_code} - {len(text)} chars")
    return r

def get_from_odds():
    url = "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds/"
    params = {"regions": "eu,uk", "markets": "h2h,totals", "oddsFormat": "decimal", "apiKey": ODDS_KEY}
    resp = requests.get(url, params=params, timeout=20)
    data = resp.json() if resp.status_code==200 else []
    print(f"ODDS {resp.status_code} remaining {resp.headers.get('x-requests-remaining')} -> {len(data)} partite")
    return data

def build_message():
    now_it = datetime.now(ITALY)
    now_str = now_it.strftime("%d/%m %H:%M")
    odds = get_from_odds()
    odds_sorted = sorted(odds, key=lambda x: x.get('commence_time',''))

    msg = f"🎯 *FUORI QUOTA - {now_str} (IT)*\n"
    msg += f"Serie A - {len(odds_sorted)} partite - Dove trovare il valore:\n\n"

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
            giorno_it = ""; giorno_label = ""; ora = ""

        if giorno_label!= giorno_corrente:
            msg += f"📅 *{giorno_it} {giorno_label}*\n"
            giorno_corrente = giorno_label

        book = m.get('bookmakers', [])
        q1 = qx = q2 = qover = ""
        fuori_quota_testo = ""

        if book:
            h2h_prices = {}
            h2h_book = {}
            for b in book:
                bname = b.get('title','Book')
                for mk in b.get('markets',[]):
                    if mk['key']=='h2h':
                        for o in mk['outcomes']:
                            h2h_prices.setdefault(o['name'], []).append(o['price'])
                            if o['name'] not in h2h_book or o['price'] > h2h_book[o['name']][0]:
                                h2h_book[o['name']] = (o['price'], bname)

            best_diff = 0
            best_name = ""
            best_price = 0
            best_avg = 0
            for name, prices in h2h_prices.items():
                if len(prices) >= 3:
                    avg = sum(prices)/len(prices)
                    best = max(prices)
                    diff = best - avg
                    if diff > best_diff:
                        best_diff = diff
                        best_name = name
                        best_price = best
                        best_avg = avg

            if best_diff >= 0.15:
                perc = (best_diff / best_avg * 100) if best_avg else 0
                dove = h2h_book.get(best_name, (best_price, "Book"))[1]
                if "Draw" in best_name:
                    fuori_quota_testo = f"💎 *FUORI QUOTA: Pareggio X @{best_price:.2f} su {dove} (media @{best_avg:.2f})*\n👉 Dove trovarla: {dove} paga +{perc:.0f}% sopra la media.\n"
                elif best_name == home_raw:
                    fuori_quota_testo = f"💎 *FUORI QUOTA: 1 {home} @{best_price:.2f} su {dove} (media @{best_avg:.2f})*\n👉 Dove trovarla: {dove} paga {home} +{perc:.0f}% sopra media.\n"
                elif best_name == away_raw:
                    fuori_quota_testo = f"💎 *FUORI QUOTA: 2 {away} @{best_price:.2f} su {dove} (media @{best_avg:.2f})*\n👉 Dove trovarla: {dove} paga {away} +{perc:.0f}% sopra media.\n"

            main_book = book[0]
            for mk in main_book.get('markets',[]):
                if mk['key']=='h2h':
                    for o in mk['outcomes']:
                        if o['name'] == home_raw:
                            q1 = f"1 @{o['price']:.2f}"
                        elif o['name'] == away_raw:
                            q2 = f"2 @{o['price']:.2f}"
                        elif "Draw" in o['name']:
                            qx = f"X @{o['price']:.2f}"
                if mk['key']=='totals':
                    for o in mk['outcomes']:
                        if 'Over' in o['name']:
                            qover = f"Over {o.get('point','')} @{o['price']:.2f}"

        msg += f"⚽ *{home} - {away}* - {ora}\n"
        msg += f"Quote: {q1} | {qx} | {q2}"
        if qover:
            msg += f" | {qover}"
        msg += f"\n"
        if fuori_quota_testo:
            msg += f"{fuori_quota_testo}\n"
        else:
            msg += f"Mercato equilibrato.\n\n"

        if len(msg) > 3800:
            msg += f"\n...altre {len(odds_sorted)-odds_sorted.index(m)-1} partite alle 14:00\n"
            break

    msg += f"\n📊 Analisi su {len(odds_sorted)} partite\n"
    msg += f"⏰ Scan: 14:00 / 20:45"
    return msg

if __name__ == "__main__":
    txt = build_message()
    print(txt)
    send_telegram(txt)
