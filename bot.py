import requests, os
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = "@fuoriquotachannel"  # <-- GIUSTO!

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

# ESEMPIO CON TUTTE LE LEGHE - qui poi colleghiamo lo scraper vero
PARTITE_DATABASE = [
    {"data":"Ven 17/10 20:45","match":"【entity-Frosinone¦canonical_name=Frosinone】 - Sassuolo","analisi":"【entity-Frosinone¦canonical_name=Frosinone】 4 over 2.5 nelle ultime 5 in casa, Sassuolo 3 gol fuori. Difese non top.","mercati":[
        {"tipo":"X","media":3.65,"best":3.85,"book":"Snai","perche":"Pareggio sottovalutato, 3 pari ultime 5 【entity-Frosinone¦canonical_name=Frosinone】"},
        {"tipo":"Over 2.5","media":1.85,"best":2.05,"book":"Goldbet","perche":"2 attacchi prolifici, 1.8 gol media"},
        {"tipo":"Gol","media":1.70,"best":1.92,"book":"Lottomatica","perche":"BTTS 7/9 partite"},
        {"tipo":"X2","media":1.55,"best":1.75,"book":"Eurobet","perche":"X2 copre Sassuolo in forma"},
    ]},
    {"data":"Sab 18/10 18:00","match":"【entity-Bologna¦canonical_name=Bologna】 - Inter","analisi":"Inter favorita ma 【entity-Bologna¦canonical_name=Bologna】 in casa ha fermato Milan e Napoli.","mercati":[
        {"tipo":"【entity-Bologna¦canonical_name=Bologna】 +1 Handicap","media":2.10,"best":2.45,"book":"Sisal","perche":"Copre pari e sconfitta misura +16%"},
        {"tipo":"Under 2.5","media":1.90,"best":2.15,"book":"Planetwin365","perche":"Inter 3 under ultime 4 fuori"},
    ]},
    {"data":"Sab 18/10 20:45","match":"Milan - Lazio","analisi":"Derby d'alta classifica, Milan in casa spinge molto.","mercati":[
        {"tipo":"1","media":2.20,"best":2.55,"book":"Snai","perche":"Milan casa forte +15% valore"},
        {"tipo":"Over 1.5 Casa","media":1.65,"best":1.90,"book":"Goldbet","perche":"Milan segna sempre in casa"},
    ]},
    {"data":"Dom 19/10 15:00","match":"Roma - Napoli","analisi":"Big match, entrambe con attacchi forti ma difese ballerine.","mercati":[
        {"tipo":"Gol","media":1.60,"best":1.85,"book":"Lottomatica","perche":"Gol quasi sicuro per entrambe"},
        {"tipo":"Over 2.5","media":1.75,"best":2.10,"book":"Eurobet","perche":"Partita da Over, 4 Over nelle ultime 5 sfide"},
    ]},
]

def build():
    txt = f"FUORI QUOTA - {datetime.now().strftime('%d/%m %H:%M')} (IT)\nSolo quote ADM Italia - Dove trovare il valore:\n\n"
    count = 0
    for p in PARTITE_DATABASE:
        blocco = f"📅 {p['data']}\n⚽ {p['match']}\n📝 {p['analisi']}\n"
        trovato = False
        for m in p['mercati']:
            if not is_adm(m['book']):
                continue
            perc = fuori_perc(m['media'], m['best'])
            if perc < 5:
                continue
            blocco += f"💎 {m['tipo']} @{m['best']} su {m['book']} (media @{m['media']}) +{perc}% - {m['perche']}\n"
            trovato = True
            count += 1
        if trovato:
            txt += blocco + "\n"
    
    if count == 0:
        txt += "Nessuna fuori quota ADM +5% al momento.\n\n"
    
    txt += "\n+18 | Solo ADM | Gioco responsabile\nInfo statistiche, non invito a scommettere."
    return txt

def main():
    text = build()
    print(text)
    r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHANNEL, "text": text})
    print(f"Telegram -> {r.status_code}")

if __name__ == "__main__":
    main()
