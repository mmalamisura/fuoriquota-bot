import os, requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = "@fuoriquota"  # metti qui il nome ESATTO del tuo canale, tipo @fuoriquotalive

print(f"TOKEN esiste? {bool(TOKEN)}")
if TOKEN:
    print(f"Prime 10 lettere token: {TOKEN[:10]}...")

# Test 1 - il bot è vivo?
r1 = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe")
print(f"getMe -> {r1.status_code} {r1.text}")

# Test 2 - prova a mandare messaggio
r2 = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
    "chat_id": CHANNEL,
    "text": "TEST DIRETTO - Se vedi questo su Telegram, il bot funziona"
})
print(f"sendMessage -> {r2.status_code} {r2.text}")
txt += "\n+18 | Solo ADM | Gioco responsabile"

requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHANNEL, "text": txt})
print("Inviato")
