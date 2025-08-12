import requests, datetime, json, traceback

WEBHOOK = "https://discord.com/api/webhooks/1404691299218620446/aP-rDO0t1NsQGnD4DeBesWN2Tw8tJhbEh4fkZUWnunMFxLNkXAtuXLfhE0LkTFXDOQ4C"  # 不要有空白或換行

# 中性策略門檻（參考你的歷史成交 & 投資建議）
RULES = {
    "BTC/TWD": {"buy_at_or_below": 3480000, "sell_at_or_above": 3680000},
    "ETH/TWD": {"buy_at_or_below": 125000, "sell_at_or_above": 134500},
    "ADA/TWD": {"buy_at_or_below": 21.8, "sell_at_or_above": 25.2},
    "SOL/TWD": {"buy_at_or_below": 5000, "sell_at_or_above": 5650},
}

PAIR_IDS = {
    "BTC/TWD": "btctwd",
    "ETH/TWD": "ethtwd",
    "ADA/TWD": "adatwd",
    "SOL/TWD": "soltwd",
}

API = "https://max-api.maicoin.com/api/v2/tickers/{}"  # e.g. .../btctwd

def send(msg: str):
    try:
        r = requests.post(WEBHOOK, json={"content": msg}, timeout=15)
        print("Discord:", r.status_code, r.text[:200])
    except Exception as e:
        print("Send Discord error:", e)

def get_last_price(symbol: str) -> float:
    pair = PAIR_IDS[symbol]
    url = API.format(pair)
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    last = float(data["ticker"]["last"])
    return last

def check_price(symbol: str, price: float):
    rules = RULES[symbol]
    if price <= rules["buy_at_or_below"]:
        send(f"💰 {symbol} 觸發【買進】條件｜現價 {price:,.4f}")
    elif price >= rules["sell_at_or_above"]:
        send(f"📈 {symbol} 觸發【賣出】條件｜現價 {price:,.4f}")
    else:
        print(f"{symbol} 未觸發｜現價 {price}")

if __name__ == "__main__":
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        for sym in PAIR_IDS.keys():
            try:
                p = get_last_price(sym)
                print(sym, "last =", p)
                check_price(sym, p)
            except Exception as e:
                print(f"[{sym}] fetch error:", e)
                send(f"⚠️ 無法取得 {sym} 報價：{e}")
        send(f"✅ 監控完成 @ {now}")
    except Exception as e:
        send("❌ 程式錯誤：\n```\n" + traceback.format_exc()[:1800] + "\n```")
