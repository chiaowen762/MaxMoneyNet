# MAX 價格監控 + Discord 提醒（讀 GitHub Secrets: WEBHOOK）
# 通知範例：
#  🟢 現在ETH價格是 123,456，符合買進條件（≤ 125,000）
#    ➡️ 建議買入 TWD 2,000（約 0.016 ETH）
#  🔴 現在BTC價格是 3,700,000，符合賣出條件（≥ 3,680,000）
#    ➡️ 建議賣出 30%

import os, requests, datetime, json, time, traceback

WEBHOOK = os.getenv("WEBHOOK", "").strip()  # 從 Secrets 讀取
if not WEBHOOK:
    print("❌ 找不到 WEBHOOK（請在 Settings → Secrets → Actions 設定 WEBHOOK）")

# —— 中性策略門檻（TWD），可直接改 —— #
# buy_below：價格 ≤ 就建議買入 buy_amount_twd
# sell_above：價格 ≥ 就建議賣出 sell_pct（小數，0.3=30%）
# buy_amount_twd：每次建議買多少新台幣（估算可買數量）
RULES = {
    "BTC/TWD": {"buy_below": 3_480_000, "buy_amount_twd": 2000, "sell_above": 3_680_000, "sell_pct": 0.30},
    "ETH/TWD": {"buy_below":   125_000, "buy_amount_twd": 2000, "sell_above":   134_500, "sell_pct": 0.30},
    "ADA/TWD": {"buy_below":        21.8, "buy_amount_twd": 2000, "sell_above":        25.2, "sell_pct": 0.30},
    "SOL/TWD": {"buy_below":      5_000, "buy_amount_twd": 2000, "sell_above":      5_650, "sell_pct": 0.30},
}

# MAX 市場代碼
MARKETS = {
    "BTC/TWD": "btctwd",
    "ETH/TWD": "ethtwd",
    "ADA/TWD": "adatwd",
    "SOL/TWD": "soltwd",
}

# 嘗試多個端點，容錯不同回應格式
ENDPOINTS = [
    "https://max-api.maicoin.com/api/v2/tickers/{m}",
    "https://max-api.maicoin.com/api/v2/tickers?markets={m}",
    "https://max.maicoin.com/api/v2/tickers/{m}",
    "https://max.maicoin.com/api/v2/tickers?markets={m}",
]

def twd(n: float) -> str:
    return f"{float(n):,.0f}"

def send(msg: str):
    if not WEBHOOK:
        print("[WARN] 未設定 WEBHOOK，以下訊息僅印出：\n", msg)
        return
    r = requests.post(WEBHOOK, json={"content": msg}, timeout=15)
    print("Discord:", r.status_code, r.text[:160])

def get_price(market_id: str) -> float:
    last_error = None
    for url_tmpl in ENDPOINTS:
        url = url_tmpl.format(m=market_id)
        try:
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                last_error = f"HTTP {r.status_code} @ {url}"
                continue
            data = json.loads(r.text.strip())

            # 形態 A：{"at":..., "ticker":{"last":"...","buy":"...","sell":"..."}}
            if isinstance(data, dict) and "ticker" in data and isinstance(data["ticker"], dict):
                t = data["ticker"]
                for key in ("last", "buy", "sell"):
                    if key in t and t[key]:
                        return float(t[key])

            # 形態 B：{"btctwd": {"ticker": {...}}, "ethtwd": {...}}
            if isinstance(data, dict) and market_id in data:
                node = data[market_id]
                if isinstance(node, dict):
                    if "ticker" in node and isinstance(node["ticker"], dict):
                        t = node["ticker"]
                        for key in ("last", "buy", "sell"):
                            if key in t and t[key]:
                                return float(t[key])
                    for key in ("last", "buy", "sell"):
                        if key in node and node[key]:
                            return float(node[key])

            # 形態 C：{"last":"..."} 或 {"price":"..."}
            if isinstance(data, dict):
                for key in ("last", "price"):
                    if key in data and data[key]:
                        return float(data[key])

            last_error = f"Unexpected JSON @ {url}: {str(data)[:160]}"
        except Exception as e:
            last_error = f"{type(e).__name__} @ {url}: {e}"
    raise RuntimeError(last_error or "unknown error")

def alert_line_buy(sym: str, price: float, rule: dict) -> str:
    amt = float(rule.get("buy_amount_twd", 0) or 0)
    qty = amt / price if price > 0 and amt > 0 else 0.0
    coin = sym.split("/")[0]
    return (
        f"🟢 現在{coin}價格是 {twd(price)}，符合買進條件（≤ {twd(rule['buy_below'])}）\n"
        f"➡️ 建議買入 TWD {twd(amt)}（約 {qty:.6f} {coin}）"
    )

def alert_line_sell(sym: str, price: float, rule: dict) -> str:
    pct = float(rule.get("sell_pct", 0) or 0)
    coin = sym.split("/")[0]
    return (
        f"🔴 現在{coin}價格是 {twd(price)}，符合賣出條件（≥ {twd(rule['sell_above'])}）\n"
        f"➡️ 建議賣出 {int(pct*100)}%"
    )

def main():
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    alerts, errors = [], []

    for sym, mid in MARKETS.items():
        rule = RULES.get(sym, {})
        try:
            price = get_price(mid)
            print(sym, "price =", price)

            if rule.get("buy_below") and price <= float(rule["buy_below"]):
                if rule.get("buy_amount_twd", 0) > 0:
                    alerts.append(alert_line_buy(sym, price, rule))

            if rule.get("sell_above") and price >= float(rule["sell_above"]):
                if rule.get("sell_pct", 0) > 0:
                    alerts.append(alert_line_sell(sym, price, rule))

        except Exception as e:
            msg = f"⚠️ 無法取得 {sym} 報價：{e}"
            print(msg)
            errors.append(msg)

        time.sleep(1)  # 降速，避免瞬間連打 API

    if alerts:
        send("**MAX 監控提醒**\n" + "\n\n".join(alerts))
    if errors:
        send("**取價錯誤摘要**\n" + "\n".join(errors))
    # 想每輪都發心跳可開啟下一行
    # send(f"✅ 心跳：本輪監控完成（{ts}）")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        send("❌ 程式錯誤：\n```\n" + traceback.format_exc()[:1800] + "\n```")
