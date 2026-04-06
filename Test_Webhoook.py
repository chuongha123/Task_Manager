import time
import requests
from datetime import datetime
import psutil

# ===== CONFIG =====
WEBHOOK_URL = "https://discord.com/api/webhooks/1368953476633329705/dQQTrK9KsRGdMAwjfjsXkkgIfPj4axgT7qYfoW80XROMl8pXLY8Xu13lfXorqyDJ0bMl".strip()
CHECK_INTERVAL = 5
THRESHOLD = 80.0

# ===== LẤY CPU/RAM =====
def get_system_usage():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    return cpu, ram

# ===== GỬI DISCORD =====
def send_discord(message: str):
    try:
        res = requests.post(WEBHOOK_URL, json={"content": message})
        print("Status:", res.status_code)

        if res.status_code != 204:
            print("Response:", res.text)

    except Exception as e:
        print("Lỗi:", e)

# ===== MONITOR =====
def monitor():
    da_canh_bao = False

    print("🚀 Bắt đầu monitor...")

    while True:
        cpu, ram = get_system_usage()
        print(f"CPU: {cpu:.1f}% | RAM: {ram:.1f}%")

        if (cpu >= THRESHOLD or ram >= THRESHOLD) and not da_canh_bao:
            msg = (
                f"🚨 CANH BAO HE THONG\n"
                f"Time: {datetime.now().strftime('%H:%M:%S')}\n"
                f"CPU: {cpu:.1f}%\n"
                f"RAM: {ram:.1f}%"
            )

            send_discord(msg)
            da_canh_bao = True

        elif cpu < THRESHOLD and ram < THRESHOLD:
            da_canh_bao = False

        time.sleep(CHECK_INTERVAL)

# ===== RUN =====
if __name__ == "__main__":
    monitor()