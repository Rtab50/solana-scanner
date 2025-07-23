from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="templates")

async def fetch_token_data():
    async with httpx.AsyncClient() as client:
        url = "https://public-api.birdeye.so/public/tokenlist?sort_by=volume_24h&sort_type=desc"
        headers = {"X-API-KEY": "public"}
        resp = await client.get(url, headers=headers)
        data = resp.json()
        return data.get("data", [])[:10]

async def analyze_token(token):
    async with httpx.AsyncClient() as client:
        address = token["address"]
        solscan_url = f"https://public-api.solscan.io/token/meta?tokenAddress={address}"
        headers = {"accept": "application/json"}
        r = await client.get(solscan_url, headers=headers)
        meta = r.json()

        return {
            "name": token.get("name"),
            "symbol": token.get("symbol"),
            "address": address,
            "verified": meta.get("isVerified", False),
            "mint_authority": meta.get("mintAuthority") is None,
            "freeze_authority": meta.get("freezeAuthority") is None,
            "holders_url": f"https://solscan.io/token/holders?token={address}"
        }

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    tokens = await fetch_token_data()
    results = []
    for token in tokens:
        try:
            res = await analyze_token(token)
            results.append(res)
        except:
            continue
    return templates.TemplateResponse("index.html", {"request": request, "tokens": results})
