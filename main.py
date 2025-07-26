from flask import Flask
import requests

app = Flask(__name__)

SOLSCAN_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3NTM0NDE2NzA4MjIsImVtYWlsIjoidGFiZXNoZ29sZEBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJhcGlWZXJzaW9uIjoidjIiLCJpYXQiOjE3NTM0NDE2NzB9.AUP36tMNi7VfW2ztMBwOit4_KI1XgDBvbVLHH7HqzUo"

# لیست دستی از چند توکن سولانا برای تست
TOKEN_ADDRESSES = [
    "Ax9hizBqVnwigABP2U5itsGAnUwqigqKf9GL3ZZZbonk",
    "GLuQ2KQtrYV8R7aZi5b6xz5vZgz5VycquNR5PCGbonk",
    "52rH2eChpf3oSgGoEM24dEA6NF7W1HvMWVj2u6MpHray",
    "6u6tvKcrqstqKXRoKaT4vEFYd3DetE3cuP4LQS3Ljups"
]

def get_token_info(token_address):
    url = f"https://public-api.solscan.io/token/meta?tokenAddress={token_address}"
    headers = {"accept": "application/json", "token": SOLSCAN_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        return data.get("name", "Unknown"), data.get("symbol", "Unknown")
    except:
        return "Unknown", "Unknown"

def get_top10_holder_percent(token_address):
    url = f"https://public-api.solscan.io/token/holders?tokenAddress={token_address}&limit=10"
    headers = {"accept": "application/json", "token": SOLSCAN_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        holders = response.json()
        total_percent = sum(holder.get("percent", 0) for holder in holders)
        return total_percent
    except:
        return None

@app.route('/')
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

    html = "<h2>🪙 توکن‌های سولانا با مجموع سهم 10 هولدر ≤ 25%</h2>"
    html += "<table border='1'><tr><th>نام</th><th>نماد</th><th>آدرس</th><th>درصد 10 هولدر</th></tr>"
    for token in results:
        html += f"<tr><td>{token['name']}</td><td>{token['symbol']}</td><td>{token['address']}</td><td>{token['top10_percent']}%</td></tr>"
    html += "</table>"

    return html

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
