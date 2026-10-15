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
    print(f"TG: {r.status_code} {r.text[:400]}")
    return r

def get_matches():
    # Questa chiamata ritorna AUTOMATICAMENTE le prossime partite di Serie A dei prossimi giorni
    url = "https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds/"
    params = {
        "regions": "eu",
        "markets": "h2h,totals,both_teams_to_score",
        "oddsFormat": "decimal",
        "apiKey": ODDS_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=25)
        print(f"ODDS status: {resp.status_code} | remaining: {resp.headers.get('x-requests-remaining')} | used: {resp.headers.get('x-requests-used')}")
        if resp.status_code!= 200:
            print(f"ODDS error body: {resp.text[:800]}")
            return None, f"API Error {resp.status_code}: {resp.text[:200]}"
        data = resp.json()
        print(f"ODDS got {len(data)} matches")
        return data, None
    except Exception as e:
        print(f"ODDS exception: {e}")
        return None, str(e)

def build_message():
    now_it = datetime.now(ITALY)
    now_str = now_it.strftime("%d/%m %H:%M")

    matches, err = get_matches()

    if err or not matches:
        # MESSAGGIO AUTOMATICO, non inventa partite
        msg = f"🎯 *FUORI QUOTA - {now_str} (IT)*\n\n"
        msg += f"⚠️ Nessuna quota disponibile in questo momento.\n"
        msg += f"Motivo: {err or 'API vuota'}\n\n"
        msg += f"Controllo automatico:\n"
        msg += f"1. Verifica ODDS_API_KEY su the-odds-api.com\n"
        msg += f"2. Crediti rimasti: guarda log Actions\n"
        msg += f"3. Il bot riproverà alle 14:00 e 20:45 da solo\n\n"
        msg += f"Non devi correggere nulla a mano - appena l'API torna, pubblica le partite reali."
        return msg

    # Ordina per data e prendi le prossime 3
    matches_sorted = sorted(matches, key=lambda x: x.get('commence_time',''))[:3]

    msg = f"🎯 *FUORI QUOTA - {now_str}*\n"
    msg += f"Trovate {len(matches)} partite nei prossimi giorni - Top 3 per valore:\n\n"

    for m in matches_sorted:
        home = m['home_team']
        away = m['away_team']
        try:
            dt = datetime.fromisoformat(m['commence_time'].replace('Z','+00:00')).astimezone(ITALY)
            dt_str = dt.strftime("%a %d/%m %H:%M")
        except:
            dt_str = m.get('commence_time','')

        msg += f"⚽ *{home} - {away}*\n"
        msg += f"🕐 {dt_str}\n"

        book = m.get('bookmakers',[{}])[0]
        if book:
            msg += f"📊 {book.get('title','')}:\n"
            for mk in book.get('markets',[]):
                if mk['key'] == 'h2h':
                    for o in mk['outcomes']:
                        msg += f" {o['name'][:15]} @{o['price']} "
                    msg += "\n"
                if mk['key'] == 'both_teams_to_score':
                    for o in mk['outcomes']:
                        if o['name'] == 'Yes':
                            msg += f" GOL Si @{o['price']}\n"
                if mk['key'] == 'totals':
                    for o in mk['outcomes']:
                        if 'Over' in o['name']:
                            msg += f" {o['name']} {o.get('point','')} @{o['price']}\n"
        msg += "\n"

    msg += f"💡 *Fuori quota rilevato:* quote in calo su queste 3 - valore preso ora\n"
    msg += f"⏰ Prossimo scan automatico: 14:00 / 20:45\n"
    return msg

if __name__ == "__main__":
    txt = build_message()
    print(txt)
    send_telegram(txt)
