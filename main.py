from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_URL = "https://public-api.birdeye.so/public/tokenlist?sort_by=volume_h24"
HEADERS = {"X-API-KEY": "INSERT_YOUR_BIRDEYE_API_KEY_HERE"}

def fetch_tokens():
    try:
        response = requests.get(API_URL, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("data", {}).get("tokens", [])
    except:
        return []
    return []

def filter_tokens(tokens, filters):
    result = []
    for token in tokens:
        symbol = token.get("symbol", "")
        verified = token.get("is_verified", False)
        lp_locked = not token.get("lp_honeypot", True)
        mint_auth = not token.get("can_mint", True)
        freeze_auth = not token.get("can_freeze", True)
        holders = token.get("holders", 0)
        market_cap = token.get("market_cap", 0)
        price = token.get("price_usd", 0)
        volume = token.get("volume_h1", None)
        price_change = token.get("price_change_h1", None)

        if filters["verified"] and not verified:
            continue
        if filters["lp_locked"] and not lp_locked:
            continue
        if filters["mint"] and not mint_auth:
            continue
        if filters["freeze"] and not freeze_auth:
            continue
        if holders < filters["holders_min"]:
            continue
        if market_cap > filters["market_cap_max"]:
            continue
        if price < filters["price_min"] or price > filters["price_max"]:
            continue
        if volume is not None and volume < filters["volume_min"]:
            continue

        token["volume_h1"] = volume if volume is not None else "نامشخص"
        token["price_change_h1"] = price_change if price_change is not None else "نامشخص"
        result.append(token)
    return result

@app.route("/", methods=["GET", "POST"])
def index():
    filters = {
        "verified": True,
        "lp_locked": True,
        "mint": True,
        "freeze": True,
        "holders_min": 50,
        "market_cap_max": 200000,
        "volume_min": 100,
        "price_min": 0,
        "price_max": 1
    }

    if request.method == "POST":
        for key in filters:
            if isinstance(filters[key], bool):
                filters[key] = request.form.get(key) == "on"
            elif isinstance(filters[key], int) or isinstance(filters[key], float):
                filters[key] = type(filters[key])(request.form.get(key, filters[key]))

    tokens = fetch_tokens()
    filtered = filter_tokens(tokens, filters)
    return render_template("index.html", tokens=filtered, filters=filters)

if __name__ == "__main__":
    app.run(debug=True)
