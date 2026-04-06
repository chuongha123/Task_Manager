"""Task monitor realtime: chỉ cảnh báo khi CPU/RAM vượt ngưỡng."""

import os
import time
from datetime import datetime
from pathlib import Path, PurePath
from typing import Any

import psutil
import requests

OUTPUT_FILE = "task_output.txt"
MAX_DISCORD_CONTENT_LENGTH = 1900
CHECK_INTERVAL_SECONDS = 5
DEFAULT_REPORT_THRESHOLD_PERCENT = 80.0
DEFAULT_ALERT_MODE = "smart"
DEFAULT_ALERT_COOLDOWN_SECONDS = 60
DEFAULT_ALERT_DELTA_PERCENT = 5.0
LOGICAL_CPU_CORES = psutil.cpu_count(logical=True) or 1
TOP_REPORT_PROCESS_COUNT = 2
ENV_FILE_PATH = ".env"


def nap_env(path: str = ENV_FILE_PATH) -> None:
    """Nạp biến môi trường từ file .env nếu file tồn tại."""
    env_path = Path(path)
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        dong = line.strip()
        if not dong or dong.startswith("#") or "=" not in dong:
            continue
        key, value = dong.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def tao_webhook_config_tu_env() -> dict[str, Any]:
    """Tạo webhook config từ biến môi trường."""
    return {
        "url": os.getenv("DISCORD_WEBHOOK_URL", "").strip(),
        "id": os.getenv("DISCORD_WEBHOOK_ID", "").strip(),
        "token": os.getenv("DISCORD_WEBHOOK_TOKEN", "").strip(),
        "channel_id": os.getenv("DISCORD_CHANNEL_ID", "").strip(),
        "guild_id": os.getenv("DISCORD_GUILD_ID", "").strip(),
        "name": os.getenv("DISCORD_WEBHOOK_NAME", "").strip(),
    }


def lay_report_threshold(
    default_threshold: float = DEFAULT_REPORT_THRESHOLD_PERCENT,
) -> float:
    """Lay nguong report tu .env; fallback ve gia tri mac dinh."""
    raw = os.getenv("REPORT_THRESHOLD_PERCENT") or os.getenv("ALERT_THRESHOLD_PERCENT")
    if raw is None:
        return default_threshold
    try:
        nguong = float(raw)
    except ValueError:
        return default_threshold
    return max(0.0, min(100.0, nguong))


def lay_top_report_process_count(default_count: int = TOP_REPORT_PROCESS_COUNT) -> int:
    """Lay so luong tien trinh can report tu .env; fallback ve gia tri mac dinh."""
    raw = os.getenv("TOP_REPORT_PROCESS_COUNT")
    if not raw:
        return default_count
    try:
        value = int(raw)
    except ValueError:
        return default_count
    return max(1, value)


def lay_discord_enabled(default_enabled: bool = True) -> bool:
    """Lay co bat/tat gui Discord tu .env."""
    raw = (os.getenv("ENABLE_DISCORD_ALERT") or "").strip().lower()
    if not raw:
        return default_enabled
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    return default_enabled


def lay_alert_mode(default_mode: str = DEFAULT_ALERT_MODE) -> str:
    """Lay che do gui canh bao: always hoac smart."""
    mode = (os.getenv("ALERT_MODE") or default_mode).strip().lower()
    if mode not in {"always", "smart"}:
        return default_mode
    return mode


def lay_alert_cooldown(default_seconds: int = DEFAULT_ALERT_COOLDOWN_SECONDS) -> int:
    """Lay cooldown giua 2 lan gui canh bao (giay)."""
    raw = os.getenv("ALERT_COOLDOWN_SECONDS")
    if not raw:
        return default_seconds
    try:
        value = int(raw)
    except ValueError:
        return default_seconds
    return max(0, value)


def lay_alert_delta(default_delta: float = DEFAULT_ALERT_DELTA_PERCENT) -> float:
    """Lay nguong bien dong de gui lai trong che do smart."""
    raw = os.getenv("ALERT_DELTA_PERCENT")
    if not raw:
        return default_delta
    try:
        value = float(raw)
    except ValueError:
        return default_delta
    return max(0.0, value)


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


def lay_so_lieu_he_thong() -> tuple[float, float, float, float]:
    """Lay CPU va RAM toan he thong (phan tram + GB)."""
    cpu_percent = float(psutil.cpu_percent(interval=1))
    ram = psutil.virtual_memory()
    ram_percent = float(ram.percent)
    ram_used_gb = float(ram.used / (1024**3))
    ram_total_gb = float(ram.total / (1024**3))
    return cpu_percent, ram_percent, ram_used_gb, ram_total_gb


def lay_du_lieu_tien_trinh(sample_seconds: float = 0.2) -> list[dict[str, Any]]:
    """Lay du lieu process thô phuc vu xep hang CPU va RAM."""
    # Prime CPU counter de lan do sau co du lieu gan thuc te hon.
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    time.sleep(sample_seconds)

    ds_tien_trinh: list[dict[str, Any]] = []
    for proc in psutil.process_iter(["pid", "name", "memory_percent", "exe", "cmdline"]):
        try:
            thong_tin = proc.info
            cpu_percent = float(proc.cpu_percent(interval=None) or 0.0)
            ram_percent = float(thong_tin.get("memory_percent") or 0.0)
            ram_mb = float(proc.memory_info().rss / (1024**2))
            ten_tien_trinh = str(thong_tin.get("name") or "<unknown>")
            exe_path = str(thong_tin.get("exe") or "").strip()
            cmdline = [
                str(token) for token in (thong_tin.get("cmdline") or []) if str(token).strip()
            ]
            ds_tien_trinh.append(
                {
                    "pid": thong_tin.get("pid"),
                    "name": ten_tien_trinh,
                    "exe_path": exe_path,
                    "cmdline": cmdline,
                    "cpu_percent": cpu_percent,
                    "cpu_percent_system_share": cpu_percent / LOGICAL_CPU_CORES,
                    "ram_percent": ram_percent,
                    "ram_mb": ram_mb,
                    "score": (cpu_percent / LOGICAL_CPU_CORES) + ram_percent,
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return ds_tien_trinh


def group_tien_trinh_theo_ung_dung(ds_tien_trinh: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Gom PID theo executable path; fallback ve ten process."""
    grouped: dict[str, dict[str, Any]] = {}
    for p in ds_tien_trinh:
        ten = str(p.get("name") or "<unknown>")
        exe_path = str(p.get("exe_path") or "").strip()
        cmdline = [str(token) for token in (p.get("cmdline") or []) if str(token).strip()]
        exe_name = PurePath(exe_path).name.lower() if exe_path else ""

        key = f"exe:{exe_path.lower()}" if exe_path else f"name:{ten.lower()}"
        nhan_ung_dung = PurePath(exe_path).name if exe_path else ten

        # Tach nhom chi tiet hon cho Java/Python theo script/jar.
        if exe_name.startswith("java") and cmdline:
            chi_tiet = ""
            if "-jar" in cmdline:
                vi_tri = cmdline.index("-jar")
                if vi_tri + 1 < len(cmdline):
                    chi_tiet = PurePath(cmdline[vi_tri + 1]).name
            if not chi_tiet:
                for token in cmdline[1:]:
                    if not token.startswith("-"):
                        chi_tiet = token
                        break
            if chi_tiet:
                key = f"java:{chi_tiet.lower()}"
                nhan_ung_dung = f"java:{chi_tiet}"
        elif exe_name.startswith("python") and len(cmdline) > 1:
            script_name = PurePath(cmdline[1]).name
            if script_name:
                key = f"python:{script_name.lower()}"
                nhan_ung_dung = f"python:{script_name}"

        if key not in grouped:
            grouped[key] = {
                "name": nhan_ung_dung,
                "exe_path": exe_path,
                "cpu_percent": 0.0,
                "cpu_percent_system_share": 0.0,
                "ram_percent": 0.0,
                "ram_mb": 0.0,
                "process_count": 0,
                "sample_pids": [],
            }

        g = grouped[key]
        g["cpu_percent"] += float(p.get("cpu_percent") or 0.0)
        g["cpu_percent_system_share"] += float(p.get("cpu_percent_system_share") or 0.0)
        g["ram_percent"] += float(p.get("ram_percent") or 0.0)
        g["ram_mb"] += float(p.get("ram_mb") or 0.0)
        g["process_count"] += 1
        if len(g["sample_pids"]) < 3 and p.get("pid") is not None:
            g["sample_pids"].append(p["pid"])

    return list(grouped.values())


def lay_top_cpu(
    ds_ung_dung: list[dict[str, Any]], limit: int = 5
) -> list[dict[str, Any]]:
    """Xep hang top ung dung theo CPU (quy doi tren toan he thong)."""
    return sorted(
        ds_ung_dung,
        key=lambda p: (
            p["cpu_percent_system_share"],
            p["cpu_percent"],
            p["ram_percent"],
        ),
        reverse=True,
    )[:limit]


def lay_top_ram(
    ds_ung_dung: list[dict[str, Any]], limit: int = 5
) -> list[dict[str, Any]]:
    """Xep hang top ung dung theo RAM."""
    return sorted(
        ds_ung_dung,
        key=lambda p: (p["ram_percent"], p["ram_mb"], p["cpu_percent_system_share"]),
        reverse=True,
    )[:limit]


def tao_dong_top_tien_trinh(
    top_cpu: list[dict[str, Any]], top_ram: list[dict[str, Any]]
) -> list[str]:
    """Tao text cho 2 bang: top CPU va top RAM."""
    dong = [
        f"Ghi chu: CPU(process) co the >100% neu app dung nhieu core (may co {LOGICAL_CPU_CORES} core).",
        "Top 5 ung dung chiem CPU cao nhat (group theo executable):",
    ]

    if top_cpu:
        for idx, p in enumerate(top_cpu, start=1):
            dong.append(
                f"  {idx}. {p['name']} | "
                f"PIDs: {p['process_count']} ({', '.join(str(pid) for pid in p['sample_pids'])}) | "
                f"CPU(process) {p['cpu_percent']:.1f}% | "
                f"CPU(he thong) ~{p['cpu_percent_system_share']:.1f}% | "
                f"RAM {p['ram_percent']:.1f}% (~{p['ram_mb']:.0f} MB)"
            )
    else:
        dong.append("  Khong co du lieu CPU.")

    dong.append("Top 5 ung dung chiem RAM cao nhat (group theo executable):")
    if top_ram:
        for idx, p in enumerate(top_ram, start=1):
            dong.append(
                f"  {idx}. {p['name']} | "
                f"PIDs: {p['process_count']} ({', '.join(str(pid) for pid in p['sample_pids'])}) | "
                f"RAM {p['ram_percent']:.1f}% (~{p['ram_mb']:.0f} MB) | "
                f"CPU(process) {p['cpu_percent']:.1f}% | "
                f"CPU(he thong) ~{p['cpu_percent_system_share']:.1f}%"
            )
    else:
        dong.append("  Khong co du lieu RAM.")
    return dong


def tao_thong_diep_canh_bao(
    cpu_percent: float,
    ram_percent: float,
    ram_used_gb: float,
    ram_total_gb: float,
    threshold: float,
    top_cpu: list[dict[str, Any]],
    top_ram: list[dict[str, Any]],
) -> str:
    """Tạo nội dung cảnh báo gửi Discord."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dong = [
        f"[{timestamp}] CANH BAO SU DUNG TAI NGUYEN",
        f"- CPU tong: {cpu_percent:.1f}%",
        f"- RAM tong: {ram_percent:.1f}% ({ram_used_gb:.1f}/{ram_total_gb:.1f} GB)",
        f"- Nguong canh bao: {threshold:.1f}%",
    ]
    dong.append("")
    dong.extend(tao_dong_top_tien_trinh(top_cpu, top_ram))

    return "\n".join(dong)


def gui_len_discord(webhook_url: str, noi_dung: str) -> tuple[int, str]:
    """Gửi báo cáo text lên Discord webhook."""
    noi_dung_gui = (
        noi_dung
        if len(noi_dung) <= MAX_DISCORD_CONTENT_LENGTH
        else f"{noi_dung[:MAX_DISCORD_CONTENT_LENGTH]}\n... (đã cắt bớt)"
    )
    response = requests.post(
        webhook_url,
        json={"content": f"```text\n{noi_dung_gui}\n```"},
        timeout=15,
    )
    return response.status_code, response.text


def ghi_file(path: str, noi_dung: str) -> None:
    """Ghi báo cáo ra file UTF-8."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(noi_dung)


def monitor_realtime(
    threshold: float,
    interval_seconds: int,
    max_cycles: int | None = None,
    alert_mode: str = DEFAULT_ALERT_MODE,
    alert_cooldown_seconds: int = DEFAULT_ALERT_COOLDOWN_SECONDS,
    alert_delta_percent: float = DEFAULT_ALERT_DELTA_PERCENT,
    top_report_process_count: int = TOP_REPORT_PROCESS_COUNT,
    discord_enabled: bool = True,
) -> None:
    """Theo dõi realtime và chỉ gửi cảnh báo khi CPU/RAM vượt ngưỡng."""
    webhook_url = lay_webhook_url(tao_webhook_config_tu_env())
    if not discord_enabled:
        print("Da tat gui Discord (ENABLE_DISCORD_ALERT=false).")
    elif not webhook_url:
        print("Chua cau hinh webhook trong .env, se theo doi nhung khong gui Discord.")

    da_canh_bao = False
    lan_gui_cuoi = 0.0
    cpu_lan_gui_cuoi: float | None = None
    ram_lan_gui_cuoi: float | None = None
    so_chu_ky = 0

    while True:
        cpu_percent, ram_percent, ram_used_gb, ram_total_gb = lay_so_lieu_he_thong()
        du_lieu_tien_trinh = lay_du_lieu_tien_trinh()
        du_lieu_ung_dung = group_tien_trinh_theo_ung_dung(du_lieu_tien_trinh)
        top_cpu = lay_top_cpu(du_lieu_ung_dung, limit=top_report_process_count)
        top_ram = lay_top_ram(du_lieu_ung_dung, limit=top_report_process_count)
        vuot_nguong = cpu_percent >= threshold or ram_percent >= threshold
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dong_trang_thai = [
            f"[{timestamp}] CPU: {cpu_percent:.1f}% | "
            f"RAM: {ram_percent:.1f}% ({ram_used_gb:.1f}/{ram_total_gb:.1f} GB) "
            f"| Threshold: {threshold:.1f}% | Cores: {LOGICAL_CPU_CORES}"
        ]
        dong_trang_thai.extend(tao_dong_top_tien_trinh(top_cpu, top_ram))
        trang_thai = "\n".join(dong_trang_thai)
        print(trang_thai)
        ghi_file(OUTPUT_FILE, trang_thai)

        if vuot_nguong:
            can_gui = False
            if alert_mode == "always":
                can_gui = True
            elif not da_canh_bao:
                can_gui = True
            else:
                now = time.time()
                qua_cooldown = (now - lan_gui_cuoi) >= alert_cooldown_seconds
                bien_dong_lon = False
                if cpu_lan_gui_cuoi is not None and ram_lan_gui_cuoi is not None:
                    bien_dong_lon = (
                        abs(cpu_percent - cpu_lan_gui_cuoi) >= alert_delta_percent
                        or abs(ram_percent - ram_lan_gui_cuoi) >= alert_delta_percent
                    )
                can_gui = qua_cooldown or bien_dong_lon

            if can_gui:
                thong_diep = tao_thong_diep_canh_bao(
                    cpu_percent,
                    ram_percent,
                    ram_used_gb,
                    ram_total_gb,
                    threshold,
                    top_cpu,
                    top_ram,
                )
                da_canh_bao = True
                lan_gui_cuoi = time.time()
                cpu_lan_gui_cuoi = cpu_percent
                ram_lan_gui_cuoi = ram_percent
                if discord_enabled and webhook_url:
                    try:
                        status, body = gui_len_discord(webhook_url, thong_diep)
                        print(f"Da gui canh bao Discord (HTTP {status}).")
                        if body:
                            print(f"Discord response: {body}")
                    except requests.RequestException as e:
                        print(f"Gui Discord that bai: {e}")
        elif not vuot_nguong and da_canh_bao:
            print("He thong da tro lai duoi nguong. San sang canh bao moi.")
            da_canh_bao = False
            cpu_lan_gui_cuoi = None
            ram_lan_gui_cuoi = None

        so_chu_ky += 1
        if max_cycles is not None and so_chu_ky >= max_cycles:
            break
        time.sleep(interval_seconds)


def main() -> None:
    """Entry point chạy monitor realtime."""
    nap_env()
    report_threshold = lay_report_threshold()
    top_report_process_count = lay_top_report_process_count()
    discord_enabled = lay_discord_enabled()
    alert_mode = lay_alert_mode()
    alert_cooldown_seconds = lay_alert_cooldown()
    alert_delta_percent = lay_alert_delta()
    print(
        "Bat dau giam sat realtime. "
        f"Chi gui Discord khi CPU hoac RAM >= {report_threshold:.1f}%."
    )
    print(f"Chu ky kiem tra: {CHECK_INTERVAL_SECONDS} giay. Nhan Ctrl+C de dung.")
    if alert_mode == "smart":
        print(
            "Che do gui: smart "
            f"(cooldown={alert_cooldown_seconds}s, delta={alert_delta_percent:.1f}%)."
        )
    else:
        print("Che do gui: always (dang vuot nguong la gui moi chu ky).")
    print(f"Gui Discord: {'bat' if discord_enabled else 'tat'}.")
    try:
        monitor_realtime(
            threshold=report_threshold,
            interval_seconds=CHECK_INTERVAL_SECONDS,
            alert_mode=alert_mode,
            alert_cooldown_seconds=alert_cooldown_seconds,
            alert_delta_percent=alert_delta_percent,
            top_report_process_count=top_report_process_count,
            discord_enabled=discord_enabled,
        )
    except KeyboardInterrupt:
        print("\nDa dung monitor.")


if __name__ == "__main__":
    main()
