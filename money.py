import requests, datetime

WEBHOOK = "https://discord.com/api/webhooks/1404691299218620446/aP-rDO0t1NsQGnD4DeBesWN2Tw8tJhbEh4fkZUWnunMFxLNkXAtuXLfhE0LkTFXDOQ4C"  # 換成你的 Discord webhook

# 買賣條件（暫時測試用數字）
RULES = {
    "BTC/TWD": {"buy_at_or_below": 3520000, "sell_at_or_above": 3650000},
    "ETH/TWD": {"buy_at_or_below": 126000, "sell_at_or_above": 133500},
    "ADA/TWD": {"buy_at_or_below": 22, "sell_at_or_above": 25},
    "SOL/TWD": {"buy_at_or_below": 5100, "sell_at_or_above": 5600},
}

def send(msg: str):
    r = requests.post(WEBHOOK, json={"content": msg})
    print("POST to:", WEBHOOK[:70] + "...")
    print("Discord status:", r.status_code)
    print("Discord resp:", r.text)

def check_price(symbol, price):
    rules = RULES[symbol]
    if price <= rules["buy_at_or_below"]:
        send(f"💰 {symbol} 觸發買進條件：現價 {price}")
    elif price >= rules["sell_at_or_above"]:
        send(f"📈 {symbol} 觸發賣出條件：現價 {price}")

if __name__ == "__main__":
    # 假資料測試（之後會換成抓 MAX API）
    test_prices = {
        "BTC/TWD": 3500000,
        "ETH/TWD": 134000,
        "ADA/TWD": 21,
        "SOL/TWD": 5700,
    }
    for sym, price in test_prices.items():
        check_price(sym, price)
