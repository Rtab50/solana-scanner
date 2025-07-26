import requests
from flask import Flask, Response
import os

app = Flask(__name__)

SOLSCAN_API_KEY = os.getenv("SOLSCAN_API_KEY") or "YOUR_SOLSCAN_API_KEY"  # کلید خودت رو بذار

# آدرس توکن‌هایی که می‌خوای تست کنی
TOKEN_ADDRESSES = [
    "Ax9hizBqVnwigABP2U5itsGAnUwqigqKf9GL3ZZZbonk",
    "GLuQ2KQtrYV8R7aZi5b6xz5vZgz5VycquNR5PCGbonk",
    "52rH2eChpf3oSgGoEM24dEA6NF7W1HvMWVj2u6MpHray",
    "6u6tvKcrqstqKXRoKaT4vEFYd3DetE3cuP4LQS3Ljups",
    "HCJ7FBu1xzTA7ZU1XWqZ9iJRPmLFqDEuTnCGWQoCbonk",
    "9bBRFSUdVby8fD3hKMLqHo95evVH8ATqitHTpd55moon",
]

def get_token_info(address):
    url = f"https://public-api.solscan.io/token/meta?tokenAddress={address}"
    headers = {
        "accept": "application/json",
        "token": SOLSCAN_API_KEY
    }
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            return data.get("name", "Unknown"), data.get("symbol", "Unknown")
    except Exception as e:
        print(f"Error fetching token info for {address}: {e}")
    return "Unknown", "Unknown"

def get_top_holders_percent(address):
    url = f"https://public-api.solscan.io/token/holders?tokenAddress={address}&limit=10&offset=0"
    headers = {
        "accept": "application/json",
        "token": SOLSCAN_API_KEY
    }
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            holders = data if isinstance(data, list) else data.get("data", [])
            total_percent = 0
            for h in holders:
                percent = h.get("percentage", 0)
                if percent is not None:
                    total_percent += float(percent)
            return round(total_percent, 2)
    except Exception as e:
        print(f"Error fetching holders for {address}: {e}")
    return 100.0  # پیش‌فرض بالا برای حذف از لیست

@app.route("/", methods=["GET", "HEAD"])
def home():
    results = []
    for address in TOKEN_ADDRESSES:
        top10_percent = get_top_holders_percent(address)
        if top10_percent <= 25:
            name, symbol = get_token_info(address)
            results.append({
                "name": name,
                "symbol": symbol,
                "address": address,
                "top10_percent": top10_percent
            })

    # ساخت جدول خروجی
    output = "🪙 توکن‌های سولانا با مجموع سهم 10 هولدر ≤ 25%\n"
    output += "نام\tنماد\tآدرس\tدرصد 10 هولدر\n"
    for token in results:
        output += f"{token['name']}\t{token['symbol']}\t{token['address']}\t{token['top10_percent']}%\n"

    return Response(output, mimetype="text/plain")

if __name__ == "__main__":
    app.run(debug=True, port=8000)

