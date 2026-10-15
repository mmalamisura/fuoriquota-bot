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
    print(f"TG {r.status_code}")
    return r

def get_from_odds():
    url = "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds/"
    params = {"regions": "eu,uk", "markets": "h2h,totals", "oddsFormat": "decimal", "apiKey": ODDS_KEY}
    resp = requests.get(url, params=params, timeout=20)
    data = resp.json() if resp.status_code==200 else []
    print(f"ODDS {resp.status_code} remaining {resp.headers.get('x-requests-remaining')} -> {len(data)}")
    return data

def build_message():
    now_it = datetime.now(ITALY)
    now_str = now_it.strftime("%d/%m %H:%M")
    odds = get_from_odds()
    odds_sorted = sorted(odds, key=lambda x: x.get('commence_time',''))

    msg = f"🎯 *FUORI QUOTA - {now_str} (IT)*\n"
    msg += f"Serie A - {len(odds_sorted)} partite - 1X2 + Over/Under:\n\n"

    giorno_corrente = ""
    for m in odds_sorted:
        home_raw = m['home_team']
        away_raw = m['away_team']
        home = home_raw.replace('Inter 【entity-Milan¦canonical_name=AC Milan】','Inter').replace('【entity-AC Milan¦canonical_name=AC Milan】','【entity-Milan¦canonical_name=AC Milan】').replace('【entity-Atalanta BC¦canonical_name=Atalanta BC】','【entity-Atalanta¦canonical_name=Atalanta BC】').replace('【entity-AS Roma¦canonical_name=AS Roma】','【entity-Roma¦canonical_name=AS Roma】')
        away = away_raw.replace('Inter 【entity-Milan¦canonical_name=AC Milan】','Inter').replace('【entity-AC Milan¦canonical_name=AC Milan】','【entity-Milan¦canonical_name=AC Milan】').replace('【entity-Atalanta BC¦canonical_name=Atalanta BC】','【entity-Atalanta¦canonical_name=Atalanta BC】').replace('【entity-AS Roma¦canonical_name=AS Roma】','【entity-Roma¦canonical_name=AS Roma】')

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
        fuori_1x2 = ""
        fuori_over = ""

        if book:
            h2h_prices = {}
            h2h_book = {}
            over_prices = {}
            over_book = {}

            for b in book:
                bname = b.get('title','Book')
                for mk in b.get('markets',[]):
                    if mk['key']=='h2h':
                        for o in mk['outcomes']:
                            h2h_prices.setdefault(o['name'], []).append(o['price'])
                            if o['name'] not in h2h_book or o['price'] > h2h_book[o['name']][0]:
                                h2h_book[o['name']] = (o['price'], bname)
                    if mk['key']=='totals':
                        for o in mk['outcomes']:
                            if 'Over' in o['name']:
                                key = f"Over {o.get('point','')}"
                                over_prices.setdefault(key, []).append(o['price'])
                                if key not in over_book or o['price'] > over_book[key][0]:
                                    over_book[key] = (o['price'], bname, o.get('point',''))

            # Fuori quota 1X2
            best_diff = 0
            best_name = ""; best_price = 0; best_avg = 0
            for name, prices in h2h_prices.items():
                if len(prices) >= 3:
                    avg = sum(prices)/len(prices)
                    best = max(prices)
                    diff = best - avg
                    if diff > best_diff:
                        best_diff = diff; best_name = name; best_price = best; best_avg = avg
            if best_diff >= 0.15:
                perc = (best_diff / best_avg * 100) if best_avg else 0
                dove = h2h_book.get(best_name, (best_price, "Book"))[1]
                if "Draw" in best_name:
                    fuori_1x2 = f"💎 1X2: Pareggio X @{best_price:.2f} su {dove} (media @{best_avg:.2f}) +{perc:.0f}%\n"
                elif best_name == home_raw:
                    fuori_1x2 = f"💎 1X2: 1 {home} @{best_price:.2f} su {dove} (media @{best_avg:.2f}) +{perc:.0f}%\n"
                elif best_name == away_raw:
                    fuori_1x2 = f"💎 1X2: 2 {away} @{best_price:.2f} su {dove} (media @{best_avg:.2f}) +{perc:.0f}%\n"

            # Fuori quota OVER
            best_over_diff = 0
            best_over_key = ""; best_over_price = 0; best_over_avg = 0; best_over_book = ""
            for key, prices in over_prices.items():
                if len(prices) >= 3:
                    avg = sum(prices)/len(prices)
                    best = max(prices)
                    diff = best - avg
                    if diff > best_over_diff:
                        best_over_diff = diff; best_over_key = key; best_over_price = best; best_over_avg = avg
                        best_over_book = over_book[key][1]

            if best_over_diff >= 0.10:
                perc_o = (best_over_diff / best_over_avg * 100) if best_over_avg else 0
                fuori_over = f"💎 OVER: {best_over_key} @{best_over_price:.2f} su {best_over_book} (media @{best_over_avg:.2f}) +{perc_o:.0f}%\n"

            # Quote base
            main_book = book[0]
            for mk in main_book.get('markets',[]):
                if mk['key']=='h2h':
                    for o in mk['outcomes']:
                        if o['name'] == home_raw: q1 = f"1 @{o['price']:.2f}"
                        elif o['name'] == away_raw: q2 = f"2 @{o['price']:.2f}"
                        elif "Draw" in o['name']: qx = f"X @{o['price']:.2f}"
                if mk['key']=='totals':
                    for o in mk['outcomes']:
                        if 'Over' in o['name']: qover = f"Over {o.get('point','')} @{o['price']:.2f}"

        msg += f"⚽ *{home} - {away}* - {ora}\n"
        msg += f"Quote: {q1} | {qx} | {q2} | {qover}\n"
        if fuori_1x2: msg += fuori_1x2
        if fuori_over: msg += fuori_over
        if not fuori_1x2 and not fuori_over:
            msg += f"Nessun fuori quota rilevante.\n"
        msg += f"\n"

        if len(msg) > 3700:
            msg += f"...altre {len(odds_sorted)-odds_sorted.index(m)-1} partite alle 14:00\n"
            break

    msg += f"📊 Analisi 1X2 + Over/Under su {len(odds_sorted)} partite\n"
    msg += f"⏰ Prossimo scan: 14:00 / 20:45"
    return msg

if __name__ == "__main__":
    txt = build_message()
    print(txt)
    send_telegram(txt)
