import requests, os
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = "@fuoriquota"  # <--- metti il tuo canale quote
TAG_AFFILIATI = {
    "Snai": "tuo-link-snai",
    "Goldbet": "tuo-link-goldbet",
    "Lottomatica": "tuo-link-lottomatica",
    "Sisal": "tuo-link-sisal",
    "Eurobet": "tuo-link-eurobet",
    "Planetwin365": "tuo-link-planetwin",
    "Bet365.it": "tuo-link-bet365it",
}

# SOLO QUESTI SONO VALIDI - tutti gli altri vengono scartati
ADM_VALIDI = list(TAG_AFFILIATI.keys())

def is_adm_valido(nome_book):
    # Blocca NL, SE, COM, Exchange, Betfair
    if any(x in nome_book for x in ["(NL)", "(SE)", "(COM)", "Exchange", "Betfair", "Betsson", "Pinnacle"]):
        return False
    return any(adm.lower() in nome_book.lower() for adm in ADM_VALIDI)

def fuori_quota_perc(media, migliore):
    return round((migliore / media - 1) * 100, 1)

# --- QUI METTI LE TUE QUOTE - Esempio con partite di oggi ---
# Il tuo scraper deve riempire questa lista solo con quote ADM
PARTITE = [
    {
        "data": "Ven 17/10 20:45",
        "match": "【entity-Frosinone¦canonical_name=Frosinone】 - 【entity-Sassuolo¦canonical_name=Sassuolo】",
        "analisi_generale": "【entity-Frosinone¦canonical_name=Frosinone】 in casa segna tanto, 【entity-Sassuolo¦canonical_name=Sassuolo】 fuori casa 4 over nelle ultime 5. Difese non imperforabili.",
        "mercati": [
            {"tipo": "Esito X", "media_adm": 3.65, "quota_best": 3.85, "book": "Snai", "perche_valore": "X sottovalutato, media ADM 3.65, Snai offre 3.85 per pareggio tra due squadre che pareggiano spesso."},
            {"tipo": "Over 2.5", "media_adm": 1.85, "quota_best": 2.05, "book": "Goldbet", "perche_valore": "Over 2.5 alto: entrambe Over nelle ultime 3, attacco 【entity-Frosinone¦canonical_name=Frosinone】 1.8 gol/partita."},
            {"tipo": "Gol (Entrambe segnano)", "media_adm": 1.70, "quota_best": 1.92, "book": "Lottomatica", "perche_valore": "BTTS: 【entity-Frosinone¦canonical_name=Frosinone】 ha segnato in 8/9 in casa, 【entity-Sassuolo¦canonical_name=Sassuolo】 7/9 fuori."},
        ]
    },
    {
        "data": "Sab 18/10 18:00",
        "match": "【entity-Bologna¦canonical_name=Bologna】 - Inter",
        "analisi_generale": "Inter favorita ma 【entity-Bologna¦canonical_name=Bologna】 in casa ha fermato Milan e Napoli.",
        "mercati": [
            {"tipo": "1 + Handicap 【entity-Bologna¦canonical_name=Bologna】 +1", "media_adm": 2.10, "quota_best": 2.45, "book": "Eurobet", "perche_valore": "Handicap +1 【entity-Bologna¦canonical_name=Bologna】 copre pareggio e vittoria di misura Inter. Valore +16% vs media."},
            {"tipo": "X Primo Tempo", "media_adm": 2.30, "quota_best": 2.60, "book": "Sisal", "perche_valore": "Primo tempo equilibrato, Inter parte piano fuori casa."},
        ]
    },
]

def build_messaggio():
    ora = datetime.now().strftime("%d/%m %H:%M")
    txt = f"💎 FUORI QUOTA - {ora} (IT)\nSerie A - Solo quote ADM Italia - Dove trovare il valore:\n\n"
    
    for p in PARTITE:
        txt += f"📅 {p['data']}\n⚽ {p['match']}\n📝 Analisi: {p['analisi_generale']}\n"
        for m in p['mercati']:
            if not is_adm_valido(m['book']):
                continue
            perc = fuori_quota_perc(m['media_adm'], m['quota_best'])
            if perc < 5:
                continue
            link = TAG_AFFILIATI.get(m['book'], "")
            txt += f"Quote ADM {m['tipo']}: media @{m['media_adm']}\n"
            txt += f"💎 FUORI QUOTA: {m['tipo']} @{m['quota_best']} su {m['book']} (media @{m['media_adm']}) +{perc}% - {m['perche_valore']}\n"
            txt += f"Link: {link}\n\n"
    
    txt += "\n+18 | Gioco responsabile | Solo quote ADM Italia\nInfo statistiche, non invito a scommettere."
    return txt

def send():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHANNEL, "text": build_messaggio()})
    print(f"Telegram {r.status_code}: {r.text[:500]}")

if __name__ == "__main__":
    send()
