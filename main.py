import requests
from bs4 import BeautifulSoup
import time
import threading
from flask import Flask
from telegram import Bot
from telegram.parsemode import ParseMode

# CONFIGURAZIONE
TELEGRAM_BOT_TOKEN = '7767698015:AAHlONl3PBYq55xIYWCqT9CGpHe4BkIBlxQ'
TELEGRAM_CHAT_ID = '1964627141'
INTERVALLO = 30  # intervallo in secondi

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# FUNZIONE DI CONTROLLO
def controlla_sito():
    url = 'https://www.nike.com/it/launch'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    prodotti = soup.find_all('figure')
    risultati = []

    for p in prodotti:
        titolo = p.find('figcaption')
        if titolo:
            nome = titolo.get_text(strip=True)
            link = p.find('a')['href']
            link_completo = f"https://www.nike.com{link}" if link.startswith('/launch') else link
            risultati.append((nome, link_completo))

    return risultati

# INVIO MESSAGGI
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def manda_alert(nome, link):
    messaggio = f"<b>👟 Nuova scarpa trovata!</b>\n\n<b>{nome}</b>\n🔗 {link}"
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=messaggio, parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f"Errore invio Telegram: {e}", flush=True)


# CICLO PRINCIPALE
def avvia_sniper():
    visti = set()
    while True:
        try:
            risultati = controlla_sito()
            for nome, link in risultati:
                if link not in visti:
                    print(f"[+] Nuovo drop: {nome} – {link}", flush=True)
                    manda_alert(nome, link)
                    visti.add(link)
            time.sleep(INTERVALLO)
        except Exception as e:
            print(f"Errore generale: {e}", flush=True)
            time.sleep(10)

# FLASK SERVER PER RENDER
app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Sneaker Bot attivo.'

# AVVIO THREAD E SERVER
if __name__ == '__main__':
    threading.Thread(target=avvia_sniper).start()
    app.run(host="0.0.0.0", port=3000)
