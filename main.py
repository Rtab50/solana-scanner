from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route("/")
def index():
    url = "https://public-api.birdeye.so/public/tokenlist?limit=50"
    headers = {"X-API-KEY": ""}  # بدون کلید API هم معمولاً جواب می‌ده

    try:
        response = requests.get(url, headers=headers)
        tokens = response.json().get("data", [])
    except Exception as e:
        tokens = []
        print("Error fetching tokens:", e)

    return render_template("index.html", tokens=tokens)
