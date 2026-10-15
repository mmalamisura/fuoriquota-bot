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
    print(f"TG: {r.status_code}")
    return r

def get_matches():
    url = "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds/"
    params = {
        "regions": "eu",
        "markets": "h2h,btts,totals",
        "oddsFormat": "decimal",
        "apiKey": ODDS_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=25)
        print(f"ODDS status: {resp.status_code} | remaining: {resp.headers.get('x-requests-remaining')}")
        if resp.status_code!= 200:
            print(resp.text[:800])
            return None, f"API Error {resp.status_code}"
        return resp.json(), None
    except Exception as e:
        return None, str(e)

def build_message():
    now_it = datetime.now(ITALY)
    now_str = now_it.strftime("%d/%m %H:%M")
    matches, err = get_matches()

    if err or not matches:
        return f"🎯 *FUORI QUOTA - {now_str}*\n\nNessun match Serie A nelle prossime 48h. Riprovo alle 14:00 automaticamente."

    matches_sorted = sorted(matches, key=lambda x: x.get('commence_time',''))[:3]
    msg = f"🎯 *FUORI QUOTA - {now_str} (IT)*\n"
    msg += f"Top 3 partite con fuori quota:\n\n"
    for m in matches_sorted:
        home = m['home_team']; away = m['away_team']
        try:
            dt = datetime.fromisoformat(m['commence_time'].replace('Z','+00:00')).astimezone(ITALY)
            dt_str = dt.strftime("%a %d/%m %H:%M")
        except:
            dt_str = ""
        msg += f"⚽ *{home} - {away}* - {dt_str}\n"
        book = m.get('bookmakers',[{}])[0]
        for mk in book.get('markets',[]):
            if mk['key'] == 'h2h':
                for o in mk['outcomes']:
                    msg += f" {o['name'][:3]} @{o['price']}"
                msg += "\n"
            if mk['key'] == 'btts':
                for o in mk['outcomes']:
                    if o['name'] == 'Yes':
                        msg += f" GOL Si @{o['price']}\n"
            if mk['key'] == 'totals':
                for o in mk['outcomes']:
                    if 'Over' in o['name']:
                        msg += f" {o['name']} {o.get('point','')} @{o['price']}\n"
        msg += "\n"
    msg += f"💡 Fuori quota: quota GOL in calo, preso ora\n⏰ Prossimo scan: 14:00 / 20:45"
    return msg

if __name__ == "__main__":
    txt = build_message()
    print(txt)
    send_telegram(txt)
