import psutil

def tim_kiem_tien_trinh(ten_chua=None, cpu_min=0, ram_min=0):
    """
    Hàm tìm kiếm và lọc các tiến trình đang chạy.

    Args:
        ten_chua (str, optional): Từ khóa tìm kiếm trong tên tiến trình.
        cpu_min (float, optional): Ngưỡng CPU tối thiểu (%).
        ram_min (float, optional): Ngưỡng RAM tối thiểu (%).

    Returns:
        list: Danh sách các tiến trình thỏa mãn điều kiện.
    """
    ket_qua = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            # Lấy thông tin của từng tiến trình
            thong_tin = proc.info
            
            # --- BẮT ĐẦU LỌC ---
            # 1. Lọc theo tên (nếu có từ khóa)
            if ten_chua and ten_chua.lower() not in thong_tin['name'].lower():
                continue
                
            # 2. Lọc theo CPU
            if thong_tin['cpu_percent'] < cpu_min:
                continue
                
            # 3. Lọc theo RAM
            if thong_tin['memory_percent'] < ram_min:
                continue
            # --- KẾT THÚC LỌC ---
            
            # Nếu thỏa mãn tất cả, thêm vào danh sách kết quả
            ket_qua.append({
                'pid': thong_tin['pid'],
                'name': thong_tin['name'],
                'cpu_percent': thong_tin['cpu_percent'],
                'ram_percent': thong_tin['memory_percent']
            })
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Bỏ qua các tiến trình không thể truy cập hoặc đã kết thúc
            pass
    return ket_qua

# --- PHẦN THỰC THI ---
if __name__ == "__main__":
    print("="*60)
    print("CHƯƠNG TRÌNH LỌC TIẾN TRÌNH")
    print("="*60)
    
    # --- Ví dụ 1: Tìm kiếm tất cả tiến trình Chrome ---
    print("\n1. Các tiến trình có tên chứa 'chrome':")
    ds_chrome = tim_kiem_tien_trinh(ten_chua="chrome")
    if ds_chrome:
        for p in ds_chrome:
            print(f"   - PID: {p['pid']}, Tên: {p['name']}, CPU: {p['cpu_percent']:.1f}%, RAM: {p['ram_percent']:.1f}%")
    else:
        print("   Không tìm thấy tiến trình Chrome nào.")
        
    # --- Ví dụ 2: Tìm tiến trình ngốn CPU (> 5%) ---
    print("\n2. Các tiến trình sử dụng CPU > 5%:")
    ds_cpu_cao = tim_kiem_tien_trinh(cpu_min=5.0)
    if ds_cpu_cao:
        for p in ds_cpu_cao:
            print(f"   - PID: {p['pid']}, Tên: {p['name']}, CPU: {p['cpu_percent']:.1f}%, RAM: {p['ram_percent']:.1f}%")
    else:
        print("   Không có tiến trình nào sử dụng CPU > 5%.")

    # --- Ví dụ 3: Kết hợp nhiều điều kiện (tên 'python' và RAM > 2%) ---
    print("\n3. Các tiến trình Python sử dụng RAM > 2%:")
    ds_python_ram_cao = tim_kiem_tien_trinh(ten_chua="python", ram_min=2.0)
    if ds_python_ram_cao:
        for p in ds_python_ram_cao:
            print(f"   - PID: {p['pid']}, Tên: {p['name']}, CPU: {p['cpu_percent']:.1f}%, RAM: {p['ram_percent']:.1f}%")
    else:
        print("   Không tìm thấy tiến trình Python nào thỏa mãn.")