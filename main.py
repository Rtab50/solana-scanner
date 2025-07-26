from flask import Flask, render_template
import requests

app = Flask(__name__)

# 🔐 کلید API اختصاصی شما از Solscan
SOLSCAN_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3NTM0NDE2NzA4MjIsImVtYWlsIjoidGFiZXNoZ29sZEBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJhcGlWZXJzaW9uIjoidjIiLCJpYXQiOjE3NTM0NDE2NzB9.AUP36tMNi7VfW2ztMBwOit4_KI1XgDBvbVLHH7HqzUo"

# ✅ آدرس توکن‌های معتبر برای تست
TOKEN_ADDRESSES = [
    "So11111111111111111111111111111111111111112",  # Wrapped SOL
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "Es9vMFrzaCER3uYfGzmiB8jYNqLk3Z9nDWkdtSgBzE9T",  # USDT
    "BonkXoNBP5cFZk33GzoRVd3dJjx54gdNhZc6UomYqjv"     # BONK
]

def get_holder_percent(token_address):
    url = f"https://pro-api.solscan.io/v1.0/token/holders?tokenAddress={token_address}&limit=10&offset=0"
    headers = {"accept": "application/json", "token": SOLSCAN_API_KEY}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get("data"):
                holders = data["data"]
                total_percent = sum([h.get("percent", 0) for h in holders])
                return total_percent
    except Exception as e:
        print(f"Error fetching holders for {token_address}: {e}")
    return None

def get_token_metadata(address):
    url = f"https://pro-api.solscan.io/v1.0/token/meta?tokenAddress={address}"
    headers = {"accept": "application/json", "token": SOLSCAN_API_KEY}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            token_data = data.get("data")
            if token_data:
                return token_data.get("name", "Unknown"), token_data.get("symbol", "Unknown")
    except Exception as e:
        print(f"Error getting metadata for {address}: {e}")
    return "Unknown", "Unknown"

@app.route("/")
def index():
    results = []
    for addr in TOKEN_ADDRESSES:
        percent = get_holder_percent(addr)
        if percent is not None and percent <= 25:
            name, symbol = get_token_metadata(addr)
            results.append({
                "address": addr,
                "percent": round(percent, 2),
                "name": name,
                "symbol": symbol
            })
    return render_template("index.html", tokens=results)

if __name__ == "__main__":
    app.run(debug=True)
