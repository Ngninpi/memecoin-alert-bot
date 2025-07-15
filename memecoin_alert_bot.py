import requests
import time

# === CONFIGURATION ===
TELEGRAM_TOKEN = '7198209745:AAFRfYLpzwnwS6EBw7_czt4K2T2IJiv5lsw'
TELEGRAM_CHAT_ID = '5635675997'
DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/pairs/solana"
MEME_KEYWORDS = ["pepe", "doge", "elon", "shiba", "floki", "moon", "baby", "meme", "wojak"]
SEEN_TOKENS = set()

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

def is_legit(token):
    try:
        name = token['baseToken']['name'].lower()
        symbol = token['baseToken']['symbol'].lower()
        liquidity_usd = float(token.get('liquidity', {}).get('usd', 0))
        fdv = float(token.get('fdv', 0) or 0)
        volume_usd = float(token.get('volume', {}).get('h1', 0))

        if not any(k in name or k in symbol for k in MEME_KEYWORDS):
            return False
        if liquidity_usd < 1000:
            return False
        if volume_usd <= 0:
            return False
        if fdv > 1e9 or fdv == 0:
            return False
        return True
    except:
        return False

def scan_dexscreener():
    try:
        res = requests.get(DEXSCREENER_URL)
        if res.status_code != 200:
            print("Erreur DexScreener")
            return

        pairs = res.json().get("pairs", [])

        for token in pairs:
            token_id = token["pairAddress"]
            if token_id in SEEN_TOKENS:
                continue

            if is_legit(token):
                name = token["baseToken"]["name"]
                symbol = token["baseToken"]["symbol"]
                url = token["url"]
                liquidity = token.get('liquidity', {}).get('usd', "N/A")
                volume = token.get('volume', {}).get('h1', "N/A")
                fdv = token.get('fdv', "N/A")

                message = f"""
🚀 <b>Nouveau MEMECOIN LÉGITIME détecté sur Solana !</b>

🪙 <b>{name.upper()} ({symbol.upper()})</b>
💧 Liquidité : ${liquidity}
📊 Volume (1h) : ${volume}
🏷 FDV : {fdv}
🔗 <a href="{url}">Voir sur DexScreener</a>
"""
                send_telegram_alert(message)
                print("[✔️] Alerte envoyée pour :", name, symbol)

            SEEN_TOKENS.add(token_id)
    except Exception as e:
        print("Erreur de scan :", e)

if __name__ == "__main__":
    print("🤖 Bot lancé sur Render...")
    while True:
        scan_dexscreener()
        time.sleep(30)
