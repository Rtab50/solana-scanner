import requests
from flask import Flask, render_template_string

app = Flask(__name__)

# ✅ کلید API شما (درج شده مستقیم در کد)
SOLSCAN_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3NTM0NDE2NzA4MjIsImVtYWlsIjoidGFiZXNoZ29sZEBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJhcGlWZXJzaW9uIjoidjIiLCJpYXQiOjE3NTM0NDE2NzB9.AUP36tMNi7VfW2ztMBwOit4_KI1XgDBvbVLHH7HqzUo"
TOKEN_ADDRESSES = [
    "So11111111111111111111111111111111111111112",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "Es9vMFrzaCER3uYfGzmiB8jYNqLk3Z9nDWkdtSgBzE9T",
    "BonkXoNBP5cFZk33GzoRVd3dJjx54gdNhZc6UomYqjv",
]

def get_token_info(addr):
    url = f"https://pro-api.solscan.io/v2.0/token/meta"
    headers = {"accept": "application/json", "Authorization": SOLSCAN_API_KEY}
    try:
        resp = requests.get(url, headers=headers, params={"address": addr}, timeout=10)
        data = resp.json().get("data", {})
        return data.get("name", "Unknown"), data.get("symbol", "Unknown")
    except:
        return "Unknown", "Unknown"

def get_top10_holder_percent(addr):
    url = "https://pro-api.solscan.io/v2.0/token/holders"
    headers = {"accept": "application/json", "Authorization": SOLSCAN_API_KEY}
    params = {"address": addr, "page": 1, "page_size": 10}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        items = resp.json().get("data", {}).get("items", [])
        total = sum(item.get("percentage", 0.0) for item in items)
        return round(total, 2)
    except Exception as e:
        print(f"Error holders {addr}: {e}")
        return None

@app.route("/")
def index():
    tokens = []
    for addr in TOKEN_ADDRESSES:
        pct = get_top10_holder_percent(addr)
        print(f"{addr}: top10% = {pct}")
        if pct is not None and pct <= 25:
            name, symbol = get_token_info(addr)
            tokens.append({"name": name, "symbol": symbol, "address": addr, "top10_percent": pct})
    html = """<h2>🪙 توکن‌های سولانا با سهم ۱۰ هولدر اول ≤ ۲۵٪</h2>
    <table border='1'><tr><th>نام</th><th>نماد</th><th>آدرس</th><th>درصد</th></tr>
    {% for t in tokens %}<tr><td>{{t.name}}</td><td>{{t.symbol}}</td><td>{{t.address}}</td><td>{{t.top10_percent}}%</td></tr>{% endfor %}</table>
    {% if not tokens %}<p>هیچ توکنی یافت نشد.</p>{% endif %}"""
    return render_template_string(html, tokens=tokens)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
