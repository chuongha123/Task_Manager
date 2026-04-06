"""Task monitor realtime: chỉ cảnh báo khi CPU/RAM vượt ngưỡng."""

import json
import time
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any

import psutil

OUTPUT_FILE = "task_output.txt"
MAX_DISCORD_CONTENT_LENGTH = 1900
CHECK_INTERVAL_SECONDS = 5
ALERT_THRESHOLD_PERCENT = 80.0

DISCORD_WEBHOOK_CONFIG = {
  "application_id": None,
  "avatar": None,
  "channel_id": "1490627045493964853",
  "guild_id": "1490627044571353131",
  "id": "1490627150372409385",
  "name": "Spidey Bot",
  "type": 1,
  "token": "ViQ-R-pB5kMMDpgqHZITPMJU36OmNrJPFszxxGuPwxINUeB6t2gS3YJoJ4GP5B2-BrB6",
  "url": "https://discord.com/api/webhooks/1490627150372409385/ViQ-R-pB5kMMDpgqHZITPMJU36OmNrJPFszxxGuPwxINUeB6t2gS3YJoJ4GP5B2-BrB6"
}


def lay_webhook_url(config: dict[str, Any]) -> str:
    """Lấy URL webhook từ config; tự dựng từ id/token nếu cần."""
    url = str(config.get("url") or "").strip()
    if url:
        return url

    webhook_id = str(config.get("id") or "").strip()
    token = str(config.get("token") or "").strip()
    if webhook_id and token:
        return f"https://discord.com/api/webhooks/{webhook_id}/{token}"
    return ""


def tim_kiem_tien_trinh(
    ten_chua: str | None = None, cpu_min: float = 0.0, ram_min: float = 0.0
) -> list[dict[str, Any]]:
    """Tìm process theo tên, CPU và RAM."""
    ket_qua: list[dict[str, Any]] = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            thong_tin = proc.info
            ten_tien_trinh = str(thong_tin.get("name") or "")
            cpu_percent = float(thong_tin.get("cpu_percent") or 0.0)
            ram_percent = float(thong_tin.get("memory_percent") or 0.0)

            if ten_chua and ten_chua.lower() not in ten_tien_trinh.lower():
                continue
            if cpu_percent < cpu_min:
                continue
            if ram_percent < ram_min:
                continue

            ket_qua.append(
                {
                    "pid": thong_tin.get("pid"),
                    "name": ten_tien_trinh or "<unknown>",
                    "cpu_percent": cpu_percent,
                    "ram_percent": ram_percent,
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return ket_qua


def lay_so_lieu_he_thong() -> tuple[float, float]:
    """Lấy CPU và RAM toàn hệ thống."""
    cpu_percent = float(psutil.cpu_percent(interval=1))
    ram_percent = float(psutil.virtual_memory().percent)
    return cpu_percent, ram_percent


def tao_thong_diep_canh_bao(cpu_percent: float, ram_percent: float, threshold: float) -> str:
    """Tạo nội dung cảnh báo gửi Discord."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dong = [
        f"[{timestamp}] CANH BAO SU DUNG TAI NGUYEN",
        f"- CPU tong: {cpu_percent:.1f}%",
        f"- RAM tong: {ram_percent:.1f}%",
        f"- Nguong canh bao: {threshold:.1f}%",
    ]

    tien_trinh_nang = tim_kiem_tien_trinh(cpu_min=5.0, ram_min=1.0)[:10]
    if tien_trinh_nang:
        dong.append("- Top process dang tai cao:")
        for p in tien_trinh_nang:
            dong.append(
                f"  * PID {p['pid']} | {p['name']} | "
                f"CPU {p['cpu_percent']:.1f}% | RAM {p['ram_percent']:.1f}%"
            )
    else:
        dong.append("- Khong tim thay process noi bat o nguong loc hien tai.")

    return "\n".join(dong)


def gui_len_discord(webhook_url: str, noi_dung: str) -> int:
    """Gửi báo cáo text lên Discord webhook."""
    noi_dung_gui = (
        noi_dung
        if len(noi_dung) <= MAX_DISCORD_CONTENT_LENGTH
        else f"{noi_dung[:MAX_DISCORD_CONTENT_LENGTH]}\n... (đã cắt bớt)"
    )

    payload = json.dumps({"content": f"```text\n{noi_dung_gui}\n```"}).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.status


def ghi_file(path: str, noi_dung: str) -> None:
    """Ghi báo cáo ra file UTF-8."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(noi_dung)


def monitor_realtime(threshold: float, interval_seconds: int, max_cycles: int | None = None) -> None:
    """Theo dõi realtime và chỉ gửi cảnh báo khi CPU/RAM vượt ngưỡng."""
    webhook_url = lay_webhook_url(DISCORD_WEBHOOK_CONFIG)
    if not webhook_url:
        print("Gửi Discord thất bại: thiếu webhook URL.")
        return

    da_canh_bao = False
    so_chu_ky = 0

    while True:
        cpu_percent, ram_percent = lay_so_lieu_he_thong()
        vuot_nguong = cpu_percent >= threshold or ram_percent >= threshold
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        trang_thai = (
            f"[{timestamp}] CPU: {cpu_percent:.1f}% | RAM: {ram_percent:.1f}% "
            f"| Threshold: {threshold:.1f}%"
        )
        print(trang_thai)
        ghi_file(OUTPUT_FILE, trang_thai)

        if vuot_nguong and not da_canh_bao:
            thong_diep = tao_thong_diep_canh_bao(cpu_percent, ram_percent, threshold)
            da_canh_bao = True
            try:
                status = gui_len_discord(webhook_url, thong_diep)
                print(f"Da gui canh bao Discord (HTTP {status}).")
            except urllib.error.HTTPError as e:
                print(f"Gui Discord that bai: HTTP {e.code} {e.reason}")
            except (urllib.error.URLError, TimeoutError) as e:
                print(f"Gui Discord that bai: {e}")
        elif not vuot_nguong and da_canh_bao:
            print("He thong da tro lai duoi nguong. San sang canh bao moi.")
            da_canh_bao = False

        so_chu_ky += 1
        if max_cycles is not None and so_chu_ky >= max_cycles:
            break
        time.sleep(interval_seconds)


def main() -> None:
    """Entry point chạy monitor realtime."""
    print(
        "Bat dau giam sat realtime. "
        f"Chi gui Discord khi CPU hoac RAM >= {ALERT_THRESHOLD_PERCENT:.1f}%."
    )
    print(f"Chu ky kiem tra: {CHECK_INTERVAL_SECONDS} giay. Nhan Ctrl+C de dung.")
    try:
        monitor_realtime(
            threshold=ALERT_THRESHOLD_PERCENT,
            interval_seconds=CHECK_INTERVAL_SECONDS,
        )
    except KeyboardInterrupt:
        print("\nDa dung monitor.")


if __name__ == "__main__":
    main()
