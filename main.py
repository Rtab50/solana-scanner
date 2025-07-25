import requests
from flask import Flask, render_template_string

app = Flask(__name__)

# API Key Solscan
SOLSCAN_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3NTM0NDE2NzA4MjIsImVtYWlsIjoidGFiZXNoZ29sZEBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJhcGlWZXJzaW9uIjoidjIiLCJpYXQiOjE3NTM0NDE2NzB9.AUP36tMNi7VfW2ztMBwOit4_KI1XgDBvbVLHH7HqzUo"

@app.route('/')
def index():
    url = "https://api.dexscreener.com/token-profiles/latest/v1"
    try:
        response = requests.get(url, timeout=20)
        data = response.json()

        solana_tokens = [t for t in data.get('tokens', []) if t.get('chainId') == 'solana']
        selected_tokens = []

        for token in solana_tokens[:20]:  # محدود به 20 توکن اول برای سرعت
            address = token.get('tokenAddress')
            name = token.get('name')
            symbol = token.get('symbol')

            headers = {"accept": "application/json", "Authorization": f"Bearer {SOLSCAN_API_KEY}"}
            holders_url = f"https://pro-api.solscan.io/v1.0/token/holders?tokenAddress={address}&limit=10"

            try:
                holders_res = requests.get(holders_url, headers=headers, timeout=15)
                holders_data = holders_res.json()

                total_percent = 0.0
                for h in holders_data.get('data', []):
                    percent = h.get('percent', 0)
                    total_percent += percent

                if total_percent <= 25:
                    selected_tokens.append({"name": name, "symbol": symbol, "address": address, "top10_percent": round(total_percent, 2)})
            except Exception as e:
                print(f"Error getting holders for {symbol}: {e}")

        return render_template_string(TEMPLATE, tokens=selected_tokens)

    except Exception as e:
        return f"Error fetching token list: {e}"


TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Solana Tokens Filtered</title>
    <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>🪙 توکن‌های سولانا با مجموع سهم 10 هولدر ≤ 25%</h1>
    {% if tokens %}
        <table>
            <tr><th>نام</th><th>نماد</th><th>آدرس</th><th>درصد 10 هولدر</th></tr>
            {% for t in tokens %}
                <tr>
                    <td>{{ t.name }}</td>
                    <td>{{ t.symbol }}</td>
                    <td><a href="https://solscan.io/token/{{ t.address }}" target="_blank">{{ t.address }}</a></td>
                    <td>{{ t.top10_percent }}%</td>
                </tr>
            {% endfor %}
        </table>
    {% else %}
        <p>هیچ توکنی با این شرط پیدا نشد.</p>
    {% endif %}
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)


