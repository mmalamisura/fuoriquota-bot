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
    resp = requests.get(url, params=params, timeout=25)
    print(f"ODDS {resp.status_code} remaining {resp.headers.get('x-requests-remaining')} -> {len(resp.json()) if resp.status_code==200 else 0} partite")
    return resp.json() if resp.status_code==200 else []

def build_message():
    now_it = datetime.now(ITALY)
    now_str = now_it.strftime("%d/%m %H:%M")
    odds = get_from_odds()

    if not odds:
        return f"🎯 *FUORI QUOTA - {now_str} (IT)*\n\nNessuna quota al momento, riprovo alle 14:00"

    # Ordina per data e prendi TUTTE le partite dei prossimi 7 giorni (non solo 3)
    odds_sorted = sorted(odds, key=lambda x: x.get('commence_time',''))

    msg = f"🎯 *FUORI QUOTA - {now_str} (IT)*\n"
    msg += f"Serie A - {len(odds_sorted)} partite rilevate:\n\n"

    giorno_corrente = ""
    for m in odds_sorted:
        home = m['home_team'].replace('Inter Milan','Inter')
        away = m['away_team'].replace('Inter Milan','Inter')
        try:
            dt = datetime.fromisoformat(m['commence_time'].replace('Z','+00:00')).astimezone(ITALY)
            giorno_en = dt.strftime("%a")
            giorno_it = GIORNI_IT.get(giorno_en, giorno_en)
            dt_str = dt.strftime(f"{giorno_it} %d/%m %H:%M")
            giorno_label = dt.strftime("%d/%m")
        except:
            dt_str = m.get('commence_time','')
            giorno_label = ""

        # Raggruppa per giorno
        if giorno_label!= giorno_corrente:
            msg += f"📅 *{dt_str.split(' ')[0]} {giorno_label}*\n"
            giorno_corrente = giorno_label

        # Calcola fuori quota vero
        book = m.get('bookmakers', [])
        best_info = ""
        if book:
            h2h_prices = {}
            for b in book:
                for mk in b.get('markets',[]):
                    if mk['key']=='h2h':
                        for o in mk['outcomes']:
                            h2h_prices.setdefault(o['name'], []).append(o['price'])
            for name, prices in h2h_prices.items():
                if len(prices) > 2:
                    avg = sum(prices)/len(prices)
                    best = max(prices)
                    if best - avg >= 0.20:
                        best_info = f"💎 FUORI QUOTA {name} @{best} vs media {avg:.2f}"

        # Quote principali
        main_book = book[0] if book else {}
        q1x2 = ""
        qover = ""
        for mk in main_book.get('markets',[]):
            if mk['key']=='h2h':
                for o in mk['outcomes']:
                    nome = "1" if o['name']==home else "2" if o['name']==away else "X"
                    q1x2 += f"{nome}@{o['price']} "
            if mk['key']=='totals':
                for o in mk['outcomes']:
                    if 'Over' in o['name']:
                        qover = f"Over {o.get('point','')} @{o['price']}"

        msg += f"⚽ {home} - {away} - {dt_str.split(' ')[1]} {dt_str.split(' ')[2]}\n"
        msg += f" {q1x2} {qover}\n"
        if best_info:
            msg += f" {best_info}\n"
        msg += f"\n"

        # Telegram ha limite 4096 caratteri, se superiamo 10 partite tagliamo
        if len(msg) > 3500:
            msg += f"\n...e altre {len(odds_sorted)-odds_sorted.index(m)-1} partite\n"
            break

    msg += f"📊 Analisi su {len(odds_sorted)} partite quotate\n"
    msg += f"⏰ Prossimo scan automatico: 14:00 / 20:45\n"
    msg += f"_Gioco responsabile - info solo statistiche_"
    return msg

if __name__ == "__main__":
    txt = build_message()
    print(txt)
    print(f"Lunghezza messaggio: {len(txt)}")
    send_telegram(txt)
