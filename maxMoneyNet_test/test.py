import requests, os

WEBHOOK = os.getenv("WEBHOOK")

RULES = {
    "BTC/TWD": {"buy_below": 99_999_999, "buy_amount_twd": 2000, "sell_above": 0, "sell_pct": 0.30},
    "ETH/TWD": {"buy_below": 99_999_999, "buy_amount_twd": 2000, "sell_above": 0, "sell_pct": 0.30},
    "ADA/TWD": {"buy_below": 99_999_999, "buy_amount_twd": 2000, "sell_above": 0, "sell_pct": 0.30},
    "SOL/TWD": {"buy_below": 99_999_999, "buy_amount_twd": 2000, "sell_above": 0, "sell_pct": 0.30},
}

def send(msg: str):
    r = requests.post(WEBHOOK, json={"content": msg})
    print("Discord status:", r.status_code, r.text)

if __name__ == "__main__":
    for coin, r in RULES.items():
        send(f"🚨 測試提醒：{coin} 現在價格符合買進條件 → 買 {r['buy_amount_twd']} TWD")
        send(f"🚨 測試提醒：{coin} 現在價格符合賣出條件 → 賣 {r['sell_pct']*100}% 持倉")
