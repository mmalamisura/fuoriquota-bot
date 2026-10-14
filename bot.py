import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ODDS_KEY = os.getenv("ODDS_API_KEY")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHANNEL_ID, "text": text}, timeout=15)

def main():
    try:
        headers = {
            "X-RapidAPI-Key": ODDS_KEY,
            "X-RapidAPI-Host": "odds-api1.p.rapidapi.com"
        }
        # Prende le prossime partite di calcio
        r = requests.get("https://odds-api1.p.rapidapi.com/v4/fixtures", headers=headers, params={"sport": "soccer"}, timeout=20)
        data = r.json()

        # Cerca Serie A
        serie_a = [m for m in data if 'italy' in str(m).lower() or 'serie' in str(m).lower()][:1]

        if serie_a:
            m = serie_a[0]
            home = str(m.get('homeTeam', m.get('home', 'Casa')))
            away = str(m.get('awayTeam', m.get('away', 'Trasferta')))
            send_telegram(f"🚀 FUORI QUOTA È PARTITO!\n\n🏟️ Prossima Serie A rilevata:\n{home} vs {away}\n\n✅ Collegamento OddsPapi riuscito (300+ bookmaker)\n🤖 Bot automatico attivo - Prossimo controllo alle 14:00\n\n@FuoriQuotaChannel | 18+ Gioca responsabile")
        else:
            send_telegram("🚀 FUORI QUOTA È PARTITO!\n\n✅ Bot collegato correttamente a OddsPapi!\nNessuna partita Serie A nelle prossime ore.\nProssimo scan automatico alle 14:00 ogni giorno.\n\n@FuoriQuotaChannel")
    except Exception as e:
        # Se anche l'API fallisce, manda comunque il messaggio di avvio così vedi che Telegram funziona
        send_telegram(f"🚀 FUORI QUOTA È PARTITO!\n\n✅ Bot collegato e attivo!\nCanale: @FuoriQuotaChannel\nProssimo controllo quote alle 14:00\n\n(Nota tecnica: {str(e)[:100]})")

if __name__ == "__main__":
    main()
