import requests, datetime

WEBHOOK = "https://discord.com/api/webhooks/1404691299218620446/aP-rDO0t1NsQGnD4DeBesWN2Tw8tJhbEh4fkZUWnunMFxLNkXAtuXLfhE0LkTFXDOQ4C"

def send(msg: str):
    r = requests.post(WEBHOOK, json={"content": msg}, timeout=15)
    print("POST to:", WEBHOOK[:70] + "...")
    print("Discord status:", r.status_code)   # 成功多半是 204
    print("Discord resp:", r.text)

if __name__ == "__main__":
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    send(f"✅ 測試：maxMoneyNet 已連線（{now}）")
