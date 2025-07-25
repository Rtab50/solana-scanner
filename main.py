import requests
from flask import Flask, render_template_string

app = Flask(__name__)

# API Key Solscan
SOLSCAN_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3NTM0NDE2NzA4MjIsImVtYWlsIjoidGFiZXNoZ29sZEBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJhcGlWZXJzaW9uIjoidjIiLCJpYXQiOjE3NTM0NDE2NzB9.AUP36tMNi7VfW2ztMBwOit4_KI1XgDBvbVLHH7HqzUo"

@app.route('/')
def index():
    url = "https://api.dexscreener.com/token-profiles/latest/v1"
    headers = {"accept": "application/json", "Authorization": f"Bearer {SOLSCAN_API_KEY}"}
    selected_tokens = []

    try:
        response = requests.get(url, timeout=20)
        data = response.json()

        for token in data if isinstance(data, list) else data.get("tokens", []):
            if token.get('chainId') != 'solana':
                continue

            address = token.get('tokenAddress')
            if not address:
                continue

            # Step 1: گرفتن 10 هولدر برتر
            holders_url = f"https://pro-api.solscan.io/v1.0/token/holders?tokenAddress={address}&limit=10"
            try:
                holders_res = requests.get(holders_url, headers=headers, timeout=15)
                holders_data = holders_res.json()

                total_percent = sum(h.get('percent', 0) for h in holders_data.get('data', []))

                if total_percent <= 25:
                    # Step 2: گرفتن نام و نماد از Solscan
                    meta_url = f"https://pro-api.solscan.io/v1.0/token/meta?tokenAddress={address}"
                    try:
                        meta_res = requests.get(meta_url, headers=headers, timeout=10)
                        meta_data = meta_res.json().get("data", {})
                        name = meta_data.get("name", "Unknown")
                        symbol = meta_data.get("symbol", "???")
                    except Exception as e:
                        print(f"Error getting metadata for {address}: {e}")
                        name, symbol = "Unknown", "???"

                    selected_tokens.append({
                        "name": name,
                        "symbol": symbol,
                        "address": address,
                        "top10_percent": round(total_percent, 2)
                    })
            except Exception as e:
                print(f"Error getting holders for {address}: {e}")

        return render_template_string(TEMPLATE, tokens=selected_tokens)

    except Exception as e:
        return f"Error fetching token list: {e}"

# قالب HTML خروجی
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Solana Tokens Filtered</title>
    <style>
        body { font-family: sans-serif; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        h1 { color: #333; }
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



