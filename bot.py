import requests, os
from datetime import datetime
from zoneinfo import ZoneInfo

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = "@fuoriquotachannel"

ADM_VALIDI = ["Snai","Goldbet","Lottomatica","Sisal","Eurobet","Planetwin365","Bet365.it","William Hill IT"]
BAN = ["(NL)","(SE)","Betfair","Betsson","Pinnacle","Exchange","Unibet"]

def is_adm(book):
    if any(x.lower() in book.lower() for x in BAN):
        return False
    return any(a.lower() in book.lower() for a in ADM_VALIDI)

def fuori_perc(media, best):
    try:
        return round((best/media-1)*100,1)
    except:
        return 0

PARTITE = [
    {
        "data": "Ven 17/10 20:45",
        "match": "Frosinone - Sassuolo",
        "analisi": "ANALISI: Frosinone casa 4 Over 2.5 nelle ultime 5, 9 gol fatti. Sassuolo fuori 2.1 xG media ultime 3. Difese: 1.4 subiti Frosinone casa, 1.6 Sassuolo fuori. Precedenti 4/5 Gol+Over. Arbitro 4.2 gialli.",
        "mercati": [
            {"tipo": "X", "media": 3.65, "best": 3.85, "book": "Snai", "perche": "Pareggio sottovalutato: 3 pari in 5 casa, quota reale 3.40 vs 3.85"},
            {"tipo": "Over 2.5", "media": 1.85, "best": 2.05, "book": "Goldbet", "perche": "2 attacchi da 1.8 gol/match, difesa Frosinone 8a peggiore tiri concessi"},
            {"tipo": "Gol (BTTS)", "media": 1.70, "best": 1.92, "book": "Lottomatica", "perche": "BTTS 7/9 Frosinone e 6/7 Sassuolo fuori"},
            {"tipo": "Doppia Chance X2", "media": 1.55, "best": 1.75, "book": "Eurobet", "perche": "Sassuolo imbattuto da 4, X2 copre 68% prob."},
        ]
    },
    {
        "data": "Sab 18/10 18:00",
        "match": "Bologna - Inter",
        "analisi": "ANALISI: Bologna casa fermato Milan 1-1 e Napoli 0-0, 0.7 xGA. Inter fuori 1.2 gol ultime 4, Lautaro a secco da 3. Tattica blocco basso vs possesso. Trend 3 Under 2.5 ultime 4 Inter fuori.",
        "mercati": [
            {"tipo": "Handicap Bologna +1", "media": 2.10, "best": 2.45, "book": "Sisal", "perche": "Copre 1-0, 1-1, 2-1. Bologna perso solo di 1 in 3/4 ultimi vs Inter"},
            {"tipo": "Under 2.5", "media": 1.90, "best": 2.15, "book": "Planetwin365", "perche": "Bologna 4 Under ultime 5 casa, Inter senza profondita fuori"},
            {"tipo": "X", "media": 3.80, "best": 4.10, "book": "Snai", "perche": "Bologna pareggiato 40% vs top 6 casa"},
        ]
    },
    {
        "data": "Sab 18/10 20:45",
        "match": "Milan - Lazio",
        "analisi": "ANALISI: Milan casa 2.3 gol media, Leao 4 gol ultime 5 San Siro. Lazio fuori 1.8 subiti, difesa alta soffre ripartenze. Precedenti 4 Over 2.5 ultimi 5 San Siro. Momentum Milan 4 vittorie fila casa.",
        "mercati": [
            {"tipo": "1", "media": 2.20, "best": 2.55, "book": "Snai", "perche": "Milan favorito ma quota gonfiata, valore reale 2.20 vs 2.55"},
            {"tipo": "Over 1.5 Casa", "media": 1.65, "best": 1.90, "book": "Goldbet", "perche": "Milan segnato 2+ gol in 6/7 casa"},
        ]
    },
    {
        "data": "Dom 19/10 15:00",
        "match": "Roma - Napoli",
        "analisi": "ANALISI: Roma 1.9 gol casa, 【entity-Dybala¦canonical_name=Dybala】-【entity-Lukaku¦canonical_name=Lukaku】 6 gol in 4. Napoli fuori 2.0 fatti ma 1.5 subiti. Precedenti ultime 5 Olimpico sempre Gol. Arbitro Massa 5.1 gialli, partita nervosa.",
        "mercati": [
            {"tipo": "Gol (BTTS)", "media": 1.60, "best": 1.85, "book": "Lottomatica", "perche": "Gol in 8/9 Roma casa e 7/8 Napoli fuori"},
            {"tipo": "Over 2.5", "media": 1.75, "best": 2.10, "book": "Eurobet", "perche": "4 Over 2.5 nelle ultime 5 sfide, ritmo alto"},
            {"tipo": "Doppia Chance 1X", "media": 1.50, "best": 1.72, "book": "Sisal", "perche": "Roma imbattuta casa da 6, Napoli 2 sconfitte ultime 3 fuori"},
        ]
    },
]

def build():
    ora_ita = datetime.now(ZoneInfo("Europe/Rome")).strftime("%d/%m %H:%M")
    txt = f"FUORI QUOTA - {ora_ita} (IT)\nSolo ADM Italia - Analisi valore:\n\n"
    for p in PARTITE:
        txt += f"📅 {p['data']}\n⚽ {p['match']}\n📝 {p['analisi']}\n"
        for m in p['mercati']:
            if not is_adm(m['book']):
                continue
            perc = fuori_perc(m['media'], m['best'])
            if perc < 5:
                continue
            txt += f"💎 {m['tipo']} @{m['best']} su {m['book']} (media @{m['media']}) +{perc}% - {m['perche']}\n"
        txt += "\n"
    txt += "---\n+18 | Solo ADM Italia (Snai, Goldbet, Lottomatica, Sisal, Eurobet, Planetwin)\nGioco responsabile - Info statistiche."
    return txt

def main():
    text = build()
    print(text)
    r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHANNEL, "text": text})
    print(f"Telegram -> {r.status_code}")

if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
