
import requests
from flask import Flask, render_template

app = Flask(__name__)

SOLSCAN_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3NTM0NDE2NzA4MjIsImVtYWlsIjoidGFiZXNoZ29sZEBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJhcGlWZXJzaW9uIjoidjIiLCJpYXQiOjE3NTM0NDE2NzB9.AUP36tMNi7VfW2ztMBwOit4_KI1XgDBvbVLHH7HqzUo"

TEST_TOKENS = [
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

@app.route("/")
def index():
    selected_tokens = []

    for address in TEST_TOKENS:
        name, symbol = None, None
        total_percent = 0.0

        try:
            headers = {"accept": "application/json", "Authorization": f"Bearer {SOLSCAN_API_KEY}"}
            meta_url = f"https://pro-api.solscan.io/v1.0/token/meta?tokenAddress={address}"
            holders_url = f"https://pro-api.solscan.io/v1.0/token/holders?tokenAddress={address}&limit=10"

            meta_res = requests.get(meta_url, headers=headers, timeout=10)
            holders_res = requests.get(holders_url, headers=headers, timeout=10)

            meta_data = meta_res.json().get("data", {})
            holders_data = holders_res.json().get("data", [])

            name = meta_data.get("name", None)
            symbol = meta_data.get("symbol", None)

            for h in holders_data:
                total_percent += h.get("percent", 0)

            if total_percent <= 25:
                selected_tokens.append({
                    "name": name, "symbol": symbol, "address": address,
                    "top10_percent": round(total_percent, 2)
                })
        except Exception as e:
            print(f"Error with token {address}: {e}")

    return render_template("index.html", tokens=selected_tokens)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
