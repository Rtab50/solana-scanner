import requests
from flask import Flask, render_template_string

app = Flask(__name__)

# لیست دستی برای تست توکن‌ها
TOKEN_ADDRESSES = [
    "DGKj2gcKkrYnJYLGN89d1yStpx7r6yPkR166opx2bonk",
    "Ax9hizBqVnwigABP2U5itsGAnUwqigqKf9GL3ZZZbonk",
    "GLuQ2KQtrYV8R7aZi5b6xz5vZgz5VycquNR5PCGbonk"
]

SOLSCAN_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3NTM0NDE2NzA4MjIsImVtYWlsIjoidGFiZXNoZ29sZEBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJhcGlWZXJzaW9uIjoidjIiLCJpYXQiOjE3NTM0NDE2NzB9.AUP36tMNi7VfW2ztMBwOit4_KI1XgDBvbVLHH7HqzUo"  # کلید Solscan را اینجا وارد کن

def get_token_info(token_address):
    url = f"https://public-api.solscan.io/v1.0/token/meta?tokenAddress={token_address}"
    headers = {"accept": "application/json", "Authorization": SOLSCAN_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        return data.get("name", "Unknown"), data.get("symbol", "Unknown")
    except:
        return "Unknown", "Unknown"

def get_top10_holder_percent(token_address):
    url = f"https://public-api.solscan.io/v1.0/token/holders?tokenAddress={token_address}&limit=10"
    headers = {"accept": "application/json", "Authorization": SOLSCAN_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        holders = response.json()
        total_percent = 0.0
        for holder in holders:
            percent = holder.get("percentage", 0.0)
            total_percent += percent
        return total_percent
    except:
        return None

@app.route("/")
def index():
    selected_tokens = []

    for address in TOKEN_ADDRESSES:
        percent = get_top10_holder_percent(address)
        if percent is None:
            continue
        if percent <= 25.0:
            name, symbol = get_token_info(address)
            selected_tokens.append({
                "name": name,
                "symbol": symbol,
                "address": address,
                "top10_percent": round(percent, 2)
            })

    html = """
    <h2>🪙 توکن‌های سولانا با مجموع سهم 10 هولدر ≤ 25%</h2>
    <table border="1" cellspacing="0" cellpadding="6">
        <tr><th>نام</th><th>نماد</th><th>آدرس</th><th>درصد 10 هولدر</th></tr>
        {% for token in tokens %}
        <tr>
            <td>{{ token.name }}</td>
            <td>{{ token.symbol }}</td>
            <td>{{ token.address }}</td>
            <td>{{ token.top10_percent }}%</td>
        </tr>
        {% endfor %}
    </table>
    {% if not tokens %}
    <p>هیچ توکنی با این شرایط یافت نشد.</p>
    {% endif %}
    """
    return render_template_string(html, tokens=selected_tokens)

if __name__ == "__main__":
    app.run(debug=True)

