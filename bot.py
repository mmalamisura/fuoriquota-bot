import requests, os
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = "@fuoriquota"
ADM_VALIDI = ["Snai","Goldbet","Lottomatica","Sisal","Eurobet","Planetwin365","Bet365.it","William Hill IT"]
BAN = ["(NL)","(SE)","Betfair","Betsson","Pinnacle","Exchange"]

def is_adm(b):
    if any(x in b for x in BAN): return False
    return any(a.lower() in b.lower() for a in ADM_VALIDI)

# Esempio con analisi e mercati diversi da 1X2
PARTITE = [
    {
        "data": "Ven 17/10 20:45", "match": "Frosinone - Sassuolo",
        "analisi": "Frosinone 4 over 2.5 nelle ultime 5 in casa, Sassuolo 3 gol fatti fuori nelle ultime 3.",
        "mercati": [
            {"tipo": "X", "media": 3.65, "best": 3.85, "book": "Snai", "perche": "Pareggio sottovalutato, 3 pari nelle ultime 5 per Frosinone"},
            {"tipo": "Over 2.5", "media": 1.85, "best": 2.05, "book": "Goldbet", "perche": "Over alto per 2 attacchi prolifici"},
            {"tipo": "Gol", "media": 1.70, "best": 1.92, "book": "Lottomatica", "perche": "BTTS: entrambe a segno in 7/9 partite"},
        ]
    }
]

txt = f"💎 FUORI QUOTA - {datetime.now().strftime('%d/%m %H:%M')} (IT)\nSolo ADM Italia\n\n"
for p in PARTITE:
    txt += f"📅 {p['data']}\n⚽ {p['match']}\n📝 {p['analisi']}\n"
    for m in p['mercati']:
        if not is_adm(m['book']): continue
        perc = round((m['best']/m['media']-1)*100,1)
        if perc >=5:
            txt += f"💎 {m['tipo']} @{m['best']} su {m['book']} (media @{m['media']}) +{perc}% - {m['perche']}\n\n"

txt += "\n+18 | Solo ADM | Gioco responsabile"

requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHANNEL, "text": txt})
print("Inviato")
