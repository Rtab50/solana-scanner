from flask import Flask, render_template
import requests

app = Flask(__name__)

SOLSCAN_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # 🔐 کلید شما
SOLSCAN_API_URL = "https://pro-api.solscan.io/v2/token/holders"
DEXSCREENER_API = "https://api.dexscreener.com/token-profiles/latest/v1"

def get_tokens_from_dexscreener():
    response = requests.get(DEXSCREENER_API)
    if response.status_code == 200:
        return response.json()
    return []

def get_top10_holder_percent(token_address):
    headers = {
        "accept": "application/json",
        "token": SOLSCAN_API_KEY
    }
    params = {
        "tokenAddress": token_address,
        "limit": 10
    }
    response = requests.get(SOLSCAN_API_URL, headers=headers, params=params)
    if response.status_code != 200:
        return None
    data = response.json()
    total_percent = sum([item.get("percent", 0) for item in data.get("data", [])])
    return total_percent

@app.route('/')
def index():
    result_tokens = []
    data = get_tokens_from_dexscreener()

    for token in data[:30]:  # فقط 30 توکن اول برای کاهش فشار
        token_address = token.get("tokenAddress")
        name = token.get("label")
        symbol = token.get("label")

        if not token_address:
            continue

        holder_percent = get_top10_holder_percent(token_address)
        if holder_percent is None:
            continue

        if holder_percent <= 25:
            result_tokens.append({
                "name": name,
                "symbol": symbol,
                "address": token_address,
                "top10_percent": round(holder_percent, 2)
            })

    return render_template("index.html", tokens=result_tokens)

if __name__ == "__main__":
    app.run(debug=True)
