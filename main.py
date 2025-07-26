from flask import Flask, render_template_string
import requests

app = Flask(__name__)

SOLSCAN_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3NTM0NDE2NzA4MjIsImVtYWlsIjoidGFiZXNoZ29sZEBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJhcGlWZXJzaW9uIjoidjIiLCJpYXQiOjE3NTM0NDE2NzB9.AUP36tMNi7VfW2ztMBwOit4_KI1XgDBvbVLHH7HqzUo"

TOKEN_ADDRESSES = [
    "So11111111111111111111111111111111111111112",  # SOL (Native wrapped)
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "Es9vMFrzaCER3uYfGzmiB8jYNqLk3Z9nDWkdtSgBzE9T",  # USDT
    "BonkXoNBP5cFZk33GzoRVd3dJjx54gdNhZc6UomYqjv",  # Bonk X
]

def get_token_metadata(address):
    url = f"https://pro-api.solscan.io/v1.0/token/meta?tokenAddress={address}"
    headers = {"accept": "application/json", "token": SOLSCAN_API_KEY}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            return data.get("data", {}).get("name", "Unknown"), data.get("data", {}).get("symbol", "Unknown")
    except Exception as e:
        print(f"Error getting metadata for {address}: {e}")
    return "Unknown", "Unknown"

def get_top10_holder_percent(address):
    url = f"https://pro-api.solscan.io/v1.0/token/holders?tokenAddress={address}&limit=10"
    headers = {"accept": "application/json", "token": SOLSCAN_API_KEY}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            holders = data.get("data", [])
            total_percent = sum(holder.get("percentage", 0) for holder in holders)
            return total_percent
    except Exception as e:
        print(f"Error getting holders for {address}: {e}")
    return 0

@app.route("/")
def index():
    selected_tokens = []
    for address in TOKEN_ADDRESSES:
        percent = get_top10_holder_percent(address)
        if percent <= 25:
            name, symbol = get_token_metadata(address)
            selected_tokens.append({
                "name": name,
                "symbol": symbol,
                "address": address,
                "top10_percent": round(percent, 2)
            })
        if len(selected_tokens) >= 10:
            break

    html = """
    <h2>🪙 توکن‌های سولانا با سهم ۱۰ هولدر اول ≤ ۲۵٪</h2>
    {% if tokens %}
    <table border="1" cellpadding="5">
        <tr>
            <th>نام</th>
            <th>نماد</th>
            <th>آدرس</th>
            <th>درصد</th>
        </tr>
        {% for t in tokens %}
        <tr>
            <td>{{ t.name }}</td>
            <td>{{ t.symbol }}</td>
            <td>{{ t.address }}</td>
            <td>{{ t.top10_percent }}%</td>
        </tr>
        {% endfor %}
    </table>
    {% else %}
    <p>هیچ توکنی با این شرایط یافت نشد.</p>
    {% endif %}
    """
    return render_template_string(html, tokens=selected_tokens)

if __name__ == "__main__":
    app.run(debug=True)
