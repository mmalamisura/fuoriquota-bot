import requests, os
from datetime import datetime
from zoneinfo import ZoneInfo

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")
ODDS_KEY = os.getenv("ODDS_API_KEY")
ITALY = ZoneInfo("Europe/Rome")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHANNEL, "text": text, "parse_mode": "Markdown"}, timeout=20)
    return r

def get_from_odds():
    url = "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds/"
    params = {"regions": "eu,uk", "markets": "h2h,totals", "oddsFormat": "decimal", "apiKey": ODDS_KEY}
    resp = requests.get(url, params=params, timeout=20)
    print(f"ODDS {resp.status_code} remaining {resp.headers.get('x-requests-remaining')} - {len(resp.json())} matches")
    return resp.json() if resp.status_code==200 else []

def build_message():
    now_it = datetime.now(ITALY)
    now_str = now_it.strftime("%d/%m %H:%M")
    odds = get_from_odds()
    odds_sorted = sorted(odds, key=lambda x: x.get('commence_time',''))[:3]

    msg = f"🎯 *FUORI QUOTA - {now_str} (IT)*\n"
    msg += f"Mercato Serie A - 3 fuori quota reali:\n\n"

    for m in odds_sorted:
        home = m['home_team'].replace('Inter Milan','Inter')
        away = m['away_team'].replace('Inter Milan','Inter')
        dt = datetime.fromisoformat(m['commence_time'].replace('Z','+00:00')).astimezone(ITALY)
        dt_str = dt.strftime("%a %d/%m %H:%M")

        # Calcola fuori quota vero: migliore quota vs media
        book = m.get('bookmakers', [])
        if not book: continue

        # Prendi tutte le quote 1X2 per calcolare media
        h2h_prices = {}
        for b in book:
            for mk in b.get('markets',[]):
                if mk['key']=='h2h':
                    for o in mk['outcomes']:
                        h2h_prices.setdefault(o['name'], []).append(o['price'])

        # Trova la migliore quota (valore)
        best_msg = ""
        for name, prices in h2h_prices.items():
            if len(prices) > 1:
                avg = sum(prices)/len(prices)
                best = max(prices)
                if best - avg > 0.15: # fuori quota se 0.15 sopra media
                    best_msg = f"💎 {name} @{best} vs media @{avg:.2f} (+{best-avg:.2f})"

        msg += f"⚽ *{home} - {away}*\n"
        msg += f"🕐 {dt_str}\n"

        # Mostra quote
        main_book = book[0]
        for mk in main_book.get('markets',[]):
            if mk['key']=='h2h':
                for o in mk['outcomes']:
                    msg += f" {o['name'][:3]} @{o['price']} "
                msg += "\n"
            if mk['key']=='totals':
                for o in mk['outcomes']:
                    if 'Over' in o['name']:
                        msg += f" {o['name']} {o.get('point','')} @{o['price']} "

        if best_msg:
            msg += f"\n{best_msg}\n👉 *FUORI QUOTA RILEVATO*\n"
        else:
            # Fallback Over
            msg += f"\n👉 Mercato stabile, watchlist Over\n"
        msg += f"\n"

    msg += f"📊 Analisi automatica su {len(odds)} partite quotate da 10gg\n"
    msg += f"⏰ Prossimo scan: 14:00 / 20:45"
    return msg

if __name__ == "__main__":
    txt = build_message()
    print(txt)
    send_telegram(txt)
