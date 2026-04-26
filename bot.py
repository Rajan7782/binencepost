import requests
import time
import threading
import random
import os
from datetime import datetime
from flask import Flask

# ========= ENV =========
CMC_API_KEY = os.getenv("CMC_API_KEY")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PORT = int(os.environ.get("PORT", 10000))

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running ✅"

# ======================

COINS = [
    "BTC","ETH","USDT","SOL","BNB","XRP","DOGE","USDC","TRX","SHIB",
    "ADA","TON","AVAX","LINK","NEAR","DOT","BCH","XLM","UNI","INJ",
    "FIL","APT","ATOM","IMX","AAVE","CRO","MKR","HBAR","OP","LDO"
]

HASHTAGS = {c: f"#{c}" for c in COINS}

def get_market(symbols):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    params = {"symbol": ",".join(symbols)}
    try:
        return requests.get(url, headers=headers, params=params).json().get("data", {})
    except:
        return {}

def get_hashtags(coins):
    return " ".join([HASHTAGS.get(c, f"#{c}") for c in coins])

def generate_short():
    selected = random.sample(COINS, 3)
    data = get_market(selected)

    lines = []
    for coin in selected:
        try:
            info = data[coin]["quote"]["USD"]
            price = round(info["price"], 3)
            change = round(info["percent_change_24h"], 2)
            trend = "📈" if change > 0 else "📉"
            lines.append(f"{coin}: ${price} ({change}%) {trend}")
        except:
            pass

    hashtags = get_hashtags(selected)

    return f"""📊 MARKET SNAPSHOT

{chr(10).join(lines)}

💡 Tip: Volatility high ⚠️

{hashtags} #crypto
"""

def generate_pro():
    selected = random.sample(COINS, 2)
    data = get_market(selected)

    insights = []
    for coin in selected:
        try:
            change = data[coin]["quote"]["USD"]["percent_change_24h"]
            if change > 3:
                insights.append(f"{coin} bullish 🚀")
            elif change < -3:
                insights.append(f"{coin} bearish 📉")
            else:
                insights.append(f"{coin} sideways ⚖️")
        except:
            pass

    hashtags = get_hashtags(selected)

    return f"""🚨 MARKET INSIGHT

{' | '.join(insights)}

💡 Trade wisely

{hashtags} #crypto
"""

def post_binance(content):
    url = "https://www.binance.com/bapi/composite/v1/public/pgc/openApi/content/add"
    headers = {
        "X-Square-OpenAPI-Key": BINANCE_API_KEY,
        "Content-Type": "application/json",
        "clienttype": "binanceSkill"
    }
    try:
        res = requests.post(url, headers=headers, json={"bodyTextOnly": content})
        return res.json()["data"]["shareLink"]
    except:
        return "Post failed"

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def auto_short():
    while True:
        try:
            post = generate_short()
            link = post_binance(post)
            send(f"🤖 AUTO\n\n{post}\n\n🔗 {link}")
        except Exception as e:
            print(e)
        time.sleep(3600)

def auto_pro():
    while True:
        try:
            post = generate_pro()
            link = post_binance(post)
            send(f"🔥 PRO\n\n{post}\n\n🔗 {link}")
        except Exception as e:
            print(e)
        time.sleep(43200)

# threads start
threading.Thread(target=auto_short).start()
threading.Thread(target=auto_pro).start()

# start web server (IMPORTANT for Render)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
