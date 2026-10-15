import requests, os
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = "@fuoriquotachannel"  # <--- se ti da chat not found metti ID numerico -100...
ADM_VALIDI = ["Snai","Goldbet","Lottomatica","Sisal","Eurobet","Planetwin365","Bet365.it","William Hill IT"]
BAN = ["(NL)","(SE)","Betfair","Betsson","Pinnacle","Exchange"]

def is_adm(b):
    if any(x in b for x in BAN): 
        return False
    return any(a.lower() in b.lower() for a in ADM_VALIDI)

def fuori_perc(media, best):
    return round((best/media-1)*100,1)

# --- QUI LE TUE PARTITE - CON ANALISI ---
PARTITE = [
    {
        "data": "Ven 17/10 20:45",
        "match": "Frosinone - 【entity-Sassuolo¦canonical_name=Sassuolo】",
        "analisi": "Frosinone 4 over 2.5 nelle ultime 5 in casa, 【entity-Sassuolo¦canonical_name=Sassuolo】 3 gol fatti fuori nelle ultime 3. Difese non al top.",
        "mercati": [
            {"tipo": "X", "media": 3.65, "best": 3.85, "book": "Snai", "perche": "Pareggio sottovalutato, 3 pari ultime 5 per Frosinone"},
            {"tipo": "Over 2.5", "media": 1.85, "best": 2.05, "book": "Goldbet", "perche": "Over alto per 2 attacchi prolifici, 1.8 gol di media"},
            {"tipo": "Gol", "media": 1.70, "best": 1.92, "book": "Lottomatica", "perche": "BTTS: entrambe a segno in 7/9 partite"},
            {"tipo": "Doppia Chance X2", "media": 1.55, "best": 1.75, "book": "Eurobet", "perche": "X2 copre pari e vittoria esterna, 【entity-Sassuolo¦canonical_name=Sassuolo】 in forma"},
        ]
    },
    {
        "data": "Sab 18/10 18:00",
        "match": "【entity-Bologna¦canonical_name=Bologna】 - Inter",
        "analisi": "Inter favorita ma 【entity-Bologna¦canonical_name=Bologna】 in casa ha fermato Milan e Napoli. Partita tattica.",
        "mercati": [
            {"tipo": "Handicap 【entity-Bologna¦canonical_name=Bologna】 +1", "media": 2.10, "best": 2.45, "book": "Sisal", "perche": "Handicap +1 copre pari e sconfitta di misura, valore +16%"},
            {"tipo": "Under 2.5", "media": 1.90, "best": 2.15, "book": "Planetwin365", "perche": "Under: Inter fuori casa 3 under nelle ultime 4"},
        ]
    }
]

def build():
    ora = datetime.now().strftime("%d/%m %H:%M")
    txt = f"💎 FUORI QUOTA - {ora} (IT)\nSerie A - Solo quote ADM Italia - Dove trovare il valore:\n\n"
    for p in PARTITE:
        txt += f"📅 {p['data']}\n⚽ {p['match']}\n📝 Analisi: {p['analisi']}\n"
        for m in p['mercati']:
            if not is_adm(m['book']):
                continue
            perc = fuori_perc(m['media'], m['best'])
            if perc < 5:
                continue
            txt += f"Quote ADM {m['tipo']}: media @{m['media']}\n"
            txt += f"💎 FUORI QUOTA: {m['tipo']} @{m['best']} su {m['book']} (media @{m['media']}) +{perc}% - {m['perche']}\n\n"
    txt += "\n+18 | Gioco responsabile | Solo quote ADM Italia\nInfo statistiche, non invito a scommettere."
    return txt

def main():
    text = build()
    print(text)
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHANNEL, "text": text})
    print(f"Telegram -> {r.status_code} {r.text[:500]}")

if __name__ == "__main__":
    main()
