import requests, os
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")

def main():
    msg = """🔥 FUORI QUOTA - TURNO SERIE A 🔥

⚽ Ven 17/10 20:45 Como vs Verona
💡 1:1.95 X:3.40 2:4.10 | VALORE: GOL a 1.80 - Verona segna fuori casa 80%

⚽ Sab 18/10 12:30 Lecce vs Sassuolo  
💡 1:2.80 X:3.20 2:2.60 | VALORE: X2 a 1.55 - Lecce 4 sconfitte nelle ultime 5

⚽ Sab 18/10 15:00 Pisa vs Lazio
💡 1:4.20 X:3.60 2:1.85 | VALORE: Lazio -0.5 a 1.95

⚽ Sab 18/10 18:00 Inter vs Fiorentina
💡 1:1.75 X:4.00 2:4.80 | VALORE: GOL a 1.70 - Inter stanca Champions

⚽ Sab 18/10 20:45 Napoli vs Cremonese
💡 1:1.40 X:4.80 2:8.00 | FUORI QUOTA: Napoli -1.5 a 2.10

⚽ Dom 19/10 12:30 Cagliari vs Bologna
💡 1:3.10 X:3.30 2:2.35 | VALORE: Under 2.5 a 1.75

⚽ Dom 19/10 15:00 Genoa vs Parma
💡 1:2.10 X:3.30 2:3.60 | VALORE: 1X a 1.35

⚽ Dom 19/10 18:00 Juventus vs Roma
💡 1:2.20 X:3.40 2:3.30 | BIG MATCH: Under 2.5 a 1.70 - difese top

⏰ 3 UPDATE AL GIORNO:
09:00 - Dove scendono le quote
14:00 - Probabili formazioni
20:45 - UFFICIALI + pick finale

#SerieA #FuoriQuota"""

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id":CHANNEL,"text":msg}, timeout=15)

if __name__=="__main__":
    main()
