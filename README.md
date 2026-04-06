# Task Manager

Script Python dùng để theo dõi tài nguyên hệ thống (CPU/RAM), lọc tiến trình và gửi cảnh báo lên Discord khi vượt ngưỡng.

## Tính năng

- Theo dõi CPU và RAM theo thời gian thực
- Chỉ gửi cảnh báo khi CPU hoặc RAM vượt ngưỡng cấu hình (mặc định 80%)
- Lọc tiến trình theo tên, mức CPU và mức RAM
- Tự ghi trạng thái mới nhất vào `task_output.txt`

## Cài đặt

```bash
python3 -m venv venv
```

Chọn **một** lệnh activate phù hợp hệ điều hành:

```bash
# Linux/macOS
source venv/bin/activate

# Windows PowerShell
.\venv\Scripts\Activate.ps1
```

Sau đó cài thư viện:

```bash
pip install -r requirements.txt
```

Tạo file cấu hình môi trường:

```bash
cp .env.example .env
```

Sau đó mở `.env` và điền webhook Discord của bạn.
Bạn cũng có thể chỉnh ngưỡng cảnh báo bằng biến:

```bash
REPORT_THRESHOLD_PERCENT=80
```

## Chạy chương trình

```bash
python Task_Manager.py
```

## Ghi chú môi trường

Nếu gặp lỗi `ModuleNotFoundError: No module named 'psutil'`, hãy kiểm tra:

- Đã activate đúng môi trường `venv` theo hệ điều hành
- Hoặc chạy trực tiếp đúng interpreter của `venv`

Ví dụ:

```bash
venv/bin/python Task_Manager.py
```

