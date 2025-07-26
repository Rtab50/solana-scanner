import os
import requests
from flask import Flask, render_template_string
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

SOLSCAN_API_KEY = os.getenv("SOLSCAN_API_KEY")

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>توکن‌های امن سولانا</title></head>
<body>
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
</body>
</html>
'''

@app.route('/')
def index():
    token_addresses = [
        "Ax9hizBqVnwigABP2U5itsGAnUwqigqKf9GL3ZZZbonk",
        "GLuQ2KQtrYV8R7aZi5b6xz5vZgz5VycquNR5PCGbonk",
        "52rH2eChpf3oSgGoEM24dEA6NF7W1HvMWVj2u6MpHray",
        "6u6tvKcrqstqKXRoKaT4vEFYd3DetE3cuP4LQS3Ljups",
        "HCJ7FBu1xzTA7ZU1XWqZ9iJRPmLFqDEuTnCGWQoCbonk",
        "9bBRFSUdVby8fD3hKMLqHo95evVH8ATqitHTpd55moon",
        "6TRuKnjqCV1XXfS4kG8M8C48yqESL2vyDfNX2Pbp7WKC",
        "GWb8dSchu8wj5oPFBMBVhhFzBiaEwvHMcaKPuVq6bonk",
        "7J4ejHLtT6pCv4ec173d6HtMGa9HxSwd34596w4kBAGS",
        "J83HUgQtiow3giu342TN7uqkckBQzcg45uJnpj48VibP"
    ]

    selected_tokens = []
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {SOLSCAN_API_KEY}"
    }

    for address in token_addresses:
        try:
            # holders
            holders_url = f"https://pro-api.solscan.io/v1.0/token/holders?tokenAddress={address}&limit=10"
            holders_res = requests.get(holders_url, headers=headers, timeout=10)
            holders_data = holders_res.json()

            total_percent = 0.0
            for h in holders_data.get('data', []):
                percent = h.get('percent', 0)
                total_percent += percent

            # meta
            meta_url = f"https://pro-api.solscan.io/v1.0/token/meta?tokenAddress={address}"
            meta_res = requests.get(meta_url, headers=headers, timeout=10)
            meta_data = meta_res.json().get("data", {})
            name = meta_data.get("name", "Unknown")
            symbol = meta_data.get("symbol", "Unknown")

            if total_percent <= 25:
                selected_tokens.append({
                    "name": name,
                    "symbol": symbol,
                    "address": address,
                    "top10_percent": round(total_percent, 2)
                })

        except Exception as e:
            print(f"Error with token {address}: {e}")

    return render_template_string(TEMPLATE, tokens=selected_tokens)

if __name__ == "__main__":
    app.run(debug=True)