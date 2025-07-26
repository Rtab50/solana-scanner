from flask import Flask, render_template
import requests

app = Flask(__name__)

SOLSCAN_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3NTM0NDE2NzA4MjIsImVtYWlsIjoidGFiZXNoZ29sZEBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJhcGlWZXJzaW9uIjoidjIiLCJpYXQiOjE3NTM0NDE2NzB9.AUP36tMNi7VfW2ztMBwOit4_KI1XgDBvbVLHH7HqzUo"

# چند آدرس برای تست دستی
TOKEN_ADDRESSES = [
    "Ax9hizBqVnwigABP2U5itsGAnUwqigqKf9GL3ZZZbonk",
    "GLuQ2KQtrYV8R7aZi5b6xz5vZgz5VycquNR5PCGbonk",
    "52rH2eChpf3oSgGoEM24dEA6NF7W1HvMWVj2u6MpHray",
    "6u6tvKcrqstqKXRoKaT4vEFYd3DetE3cuP4LQS3Ljups"
]

def get_top10_holder_percent(token_address):
    url = f"https://public-api.solscan.io/token/holders?tokenAddress={token_address}&limit=10"
    headers = {
        "accept": "application/json",
        "token": SOLSCAN_API_KEY
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        holders = response.json()

        total_percent = 0
        for holder in holders:
            percent = holder.get("percent")
            if isinstance(percent, (int, float)):
                total_percent += percent

        return total_percent
    except Exception as e:
        print(f"⚠️ خطا در دریافت هولدرها برای {token_address}: {e}")
        return None

def get_token_info(token_address):
    url = f"https://public-api.solscan.io/token/meta?tokenAddress={token_address}"
    headers = {
        "accept": "application/json",
        "token": SOLSCAN_API_KEY
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        return data.get("name", "Unknown"), data.get("symbol", "Unknown")
    except Exception as e:
        print(f"⚠️ خطا در دریافت اطلاعات توکن برای {token_address}: {e}")
        return "Unknown", "Unknown"

@app.route("/")
def index():
    results = []

    for address in TOKEN_ADDRESSES:
        name, symbol = get_token_info(address)
        top10_percent = get_top10_holder_percent(address)

        if top10_percent is not None and top10_percent <= 25:
            results.append({
                "name": name,
                "symbol": symbol,
                "address": address,
                "top10_percent": round(top10_percent, 2)
            })
        else:
            print(f"⛔ حذف شد: {address} | درصد هولدرها: {top10_percent} | نام: {name}, نماد: {symbol}")

    return render_template("index.html", tokens=results)
