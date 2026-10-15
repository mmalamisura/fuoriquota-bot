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
    print(f"TG {r.status_code}")
    return r

def get_from_odds():
    url = "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds/"
    params = {"regions": "eu,uk", "markets": "h2h,totals", "oddsFormat": "decimal", "apiKey": ODDS_KEY}
    try:
        resp = requests.get(url, params=params, timeout=20)
        print(f"ODDS {resp.status_code} remaining {resp.headers.get('x-requests-remaining')} len {len(resp.text)}")
        if resp.status_code==200:
            data = resp.json()
            print(f"Trovate {len(data)} partite Serie A")
            return data
        else:
            print(resp.text[:800])
    except Exception as e:
        print(f"ODDS fail {e}")
    return None

def build_message():
    now_it = datetime.now(ITALY)
    now_str = now_it.strftime("%d/%m %H:%M")
    odds = get_from_odds()

    if not odds:
        return f"🎯 *FUORI QUOTA - {now_str}*\n\nNessuna partita trovata, riprovo alle 14:00"

    odds_sorted = sorted(odds, key=lambda x: x.get('commence_time',''))[:3]
    msg = f"🎯 *FUORI QUOTA - {now_str} (IT)*\n"
    msg += f"Serie A - {len(odds)} partite quotate (da 10gg):\n\n"
    for m in odds_sorted:
        home = m['home_team']; away = m['away_team']
        try:
            dt = datetime.fromisoformat(m['commence_time'].replace('Z','+00:00')).astimezone(ITALY)
            dt_str = dt.strftime("%a %d/%m %H:%M")
        except:
            dt_str = ""
        msg += f"⚽ *{home} - {away}* - {dt_str}\n"
        book = m.get('bookmakers',[{}])[0]
        for mk in book.get('markets',[]):
            if mk['key']=='h2h':
                for o in mk['outcomes']:
                    msg += f" {o['name'][:3]} @{o['price']}"
                msg += "\n"
            if mk['key']=='totals':
                for o in mk['outcomes']:
                    if 'Over' in o['name']:
                        msg += f" {o['name']} {o.get('point','')} @{o['price']}\n"
        msg += f" 👉 *Fuori quota rilevato* - quota in calo\n\n"
    msg += f"⏰ Prossimo scan: 14:00 / 20:45"
    return msg

if __name__ == "__main__":
    txt = build_message()
    print(txt)
    send_telegram(txt)
