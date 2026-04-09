# Hướng Dẫn Sử Dụng (bản phân phối 2 file)

Tài liệu này dành cho người chỉ có 2 file:

- `ManagerTaskMonitor.exe`
- `.env`

Mục tiêu: chạy monitor CPU/RAM nền trên Windows và gửi cảnh báo Discord theo cấu hình trong `.env`.

---

## 1) Chuẩn bị thư mục

1. Tạo 1 thư mục bất kỳ, ví dụ: `D:\ManagerTaskMonitor`
2. Copy **cả 2 file** vào cùng thư mục đó:
   - `ManagerTaskMonitor.exe`
   - `.env`
3. Kiểm tra lại tên file đúng chính tả:
   - Phải là `.env` (có dấu chấm ở đầu)
   - Không được là `.env.txt`

Gợi ý: bật hiện file ẩn trong Explorer để dễ thấy file bắt đầu bằng dấu chấm.

---

## 2) Cấu hình `.env`

Bạn có thể sửa `.env` bằng Notepad/VS Code. Mỗi lần sửa xong, dừng chương trình đang chạy và mở lại `.exe` để áp dụng cấu hình mới.

### Mẫu cấu hình cơ bản

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN

REPORT_THRESHOLD_CPU_PERCENT=85
REPORT_THRESHOLD_RAM_PERCENT=75
TOP_REPORT_PROCESS_COUNT=5

CHECK_INTERVAL_SECONDS=5
CPU_MEASURE_INTERVAL_SECONDS=1
PROCESS_SAMPLE_SECONDS=0.2

ENABLE_DISCORD_ALERT=true
ALERT_MODE=smart
ALERT_COOLDOWN_SECONDS=60
ALERT_DELTA_PERCENT=5
```

### Ý nghĩa các biến quan trọng

- `DISCORD_WEBHOOK_URL`: URL webhook Discord để gửi cảnh báo.
- `REPORT_THRESHOLD_CPU_PERCENT`: ngưỡng CPU tổng (%).
- `REPORT_THRESHOLD_RAM_PERCENT`: ngưỡng RAM tổng (%).
- `TOP_REPORT_PROCESS_COUNT`: số ứng dụng top CPU/RAM trong nội dung cảnh báo.
- `CHECK_INTERVAL_SECONDS`: thời gian sleep giữa 2 vòng monitor.
- `ENABLE_DISCORD_ALERT`: `true/false`, bật tắt gửi Discord.
- `ALERT_MODE`:
  - `smart`: chỉ gửi lại khi qua cooldown hoặc biến động lớn.
  - `always`: đang vượt ngưỡng là gửi mỗi chu kỳ.
- `ALERT_COOLDOWN_SECONDS`: khoảng nghỉ tối thiểu giữa 2 lần gửi (chế độ smart).
- `ALERT_DELTA_PERCENT`: biến động CPU/RAM (%), vượt giá trị này thì gửi lại (chế độ smart).

### Lưu ý khi sửa `.env`

- Không cần để dấu ngoặc kép (`"`), nhưng có để cũng được.
- Không thêm khoảng trắng trước/sau giá trị nếu có thể.
- Nếu webhook sai, app vẫn chạy monitor nhưng không gửi được Discord.

---

## 3) Chạy thủ công

1. Double click `ManagerTaskMonitor.exe`.
2. Ứng dụng chạy nền (không hiện cửa sổ console).
3. Khi CPU hoặc RAM vượt ngưỡng trong `.env`, webhook Discord sẽ nhận cảnh báo.

Để dừng app đang chạy:

- Mở Task Manager (`Ctrl + Shift + Esc`)
- Tìm `ManagerTaskMonitor.exe`
- Chọn `End task`

Sau đó mở lại `ManagerTaskMonitor.exe` nếu muốn chạy tiếp.

---

## 4) Tự động chạy khi đăng nhập Windows (đề nghị)

Nếu muốn mỗi lần mở máy/đăng nhập là app tự chạy:

1. Mở `Task Scheduler`
2. Chọn `Create Task...`
3. Tab `General`:
   - Name: `ManagerTaskMonitor`
   - Chọn `Run only when user is logged on`
4. Tab `Triggers` -> `New...`:
   - Begin the task: `At log on`
   - Chọn user hiện tại
5. Tab `Actions` -> `New...`:
   - Action: `Start a program`
   - Program/script: đường dẫn tới `ManagerTaskMonitor.exe`
   - Start in (optional): thư mục chứa file `.exe` và `.env` (nên điền)
6. Tab `Settings`:
   - Cho phép restart nếu fail (nếu cần)
7. `OK` để lưu.

Kiểm tra task:

- Trong `Task Scheduler Library`, tìm `ManagerTaskMonitor`
- Right click -> `Run` để test thủ công
- Xem cột `Last Run Result` để biết thành công hay lỗi.

---

## 5) Cách cập nhật cấu hình sau này

Khi cần đổi webhook/ngưỡng:

1. End task `ManagerTaskMonitor.exe` đang chạy
2. Sửa file `.env`
3. Lưu file
4. Chạy lại `ManagerTaskMonitor.exe` (hoặc `Run` lại task trong Task Scheduler)

Không cần build lại `.exe`.

---

## 6) Mang sang máy khác cần gì?

Chỉ cần:

- `ManagerTaskMonitor.exe`
- `.env`

Đặt cùng thư mục trên máy mới là chạy được.

Không cần cài Python.

---

## 7) Xử lý sự cố nhanh

### Không thấy Discord gửi cảnh báo

- Kiểm tra `DISCORD_WEBHOOK_URL` đúng hay không.
- Thử tạo webhook mới và thay lại trong `.env`.
- Đảm bảo `ENABLE_DISCORD_ALERT=true`.
- Đảm bảo máy có internet, không bị chặn Discord.

### Đã mở exe nhưng không thấy gì

- App chạy nền nên không có cửa sổ là bình thường.
- Vào Task Manager xem có process `ManagerTaskMonitor.exe` hay không.

### Đổi `.env` nhưng app không nhận

- Bạn phải dừng process cũ và mở lại exe.
- Nếu chạy qua Task Scheduler, `End` task rồi `Run` lại.

### Restart máy xong không tự chạy

- Kiểm tra task có trigger `At log on` đúng user.
- Kiểm tra Action trỏ đúng đến file `ManagerTaskMonitor.exe`.
- Kiểm tra `Start in` trùng thư mục chứa `.env`.

---

## 8) Khuyến nghị bảo mật

- Không chia sẻ `.env` cho người không tin cậy (vì chứa webhook token).
- Nếu lộ token, vào Discord tạo webhook mới và cập nhật lại ngay.

---

## 9) Tóm tắt quy trình dùng nhanh

1. Để `ManagerTaskMonitor.exe` + `.env` cùng thư mục.
2. Sửa `.env` theo nhu cầu.
3. Chạy `ManagerTaskMonitor.exe`.
4. Nếu muốn tự động khi đăng nhập, tạo Scheduled Task như mục 4.
# Huong Dan Su Dung (ban phan phoi 2 file)

Tai lieu nay danh cho nguoi chi co 2 file:

- `ManagerTaskMonitor.exe`
- `.env`

Muc tieu: chay monitor CPU/RAM nen tren Windows va gui canh bao Discord theo cau hinh trong `.env`.

---

## 1) Chuan bi thu muc

1. Tao 1 thu muc bat ky, vi du: `D:\ManagerTaskMonitor`
2. Copy **ca 2 file** vao cung thu muc do:
   - `ManagerTaskMonitor.exe`
   - `.env`
3. Kiem tra lai ten file dung chinh ta:
   - Phai la `.env` (co dau cham o dau)
   - Khong duoc la `.env.txt`

Goi y: bat hien file an trong Explorer de de thay file bat dau bang dau cham.

---

## 2) Cau hinh `.env`

Ban co the sua `.env` bang Notepad/VS Code. Moi lan sua xong, dung chuong trinh dang chay va mo lai `.exe` de ap dung cau hinh moi.

### Mau cau hinh co ban

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN

REPORT_THRESHOLD_CPU_PERCENT=85
REPORT_THRESHOLD_RAM_PERCENT=75
TOP_REPORT_PROCESS_COUNT=5

CHECK_INTERVAL_SECONDS=5
CPU_MEASURE_INTERVAL_SECONDS=1
PROCESS_SAMPLE_SECONDS=0.2

ENABLE_DISCORD_ALERT=true
ALERT_MODE=smart
ALERT_COOLDOWN_SECONDS=60
ALERT_DELTA_PERCENT=5
```

### Y nghia cac bien quan trong

- `DISCORD_WEBHOOK_URL`: URL webhook Discord de gui canh bao.
- `REPORT_THRESHOLD_CPU_PERCENT`: nguong CPU tong (%).
- `REPORT_THRESHOLD_RAM_PERCENT`: nguong RAM tong (%).
- `TOP_REPORT_PROCESS_COUNT`: so ung dung top CPU/RAM trong noi dung canh bao.
- `CHECK_INTERVAL_SECONDS`: thoi gian sleep giua 2 vong monitor.
- `ENABLE_DISCORD_ALERT`: `true/false`, bat tat gui Discord.
- `ALERT_MODE`:
  - `smart`: chi gui lai khi qua cooldown hoac bien dong lon.
  - `always`: dang vuot nguong la gui moi chu ky.
- `ALERT_COOLDOWN_SECONDS`: khoang nghi toi thieu giua 2 lan gui (che do smart).
- `ALERT_DELTA_PERCENT`: bien dong CPU/RAM (%), vuot gia tri nay thi gui lai (che do smart).

### Luu y khi sua `.env`

- Khong can de dau ngoac kep (`"`), nhung co de cung duoc.
- Khong them khoang trang truoc/sau gia tri neu co the.
- Neu webhook sai, app van chay monitor nhung khong gui duoc Discord.

---

## 3) Chay thu cong

1. Double click `ManagerTaskMonitor.exe`.
2. Ung dung chay nen (khong hien cua so console).
3. Khi CPU hoac RAM vuot nguong trong `.env`, webhook Discord se nhan canh bao.

De dung app dang chay:

- Mo Task Manager (`Ctrl + Shift + Esc`)
- Tim `ManagerTaskMonitor.exe`
- Chon `End task`

Sau do mo lai `ManagerTaskMonitor.exe` neu muon chay tiep.

---

## 4) Tu dong chay khi dang nhap Windows (de nghi)

Neu muon moi lan mo may/ dang nhap la app tu chay:

1. Mo `Task Scheduler`
2. Chon `Create Task...`
3. Tab `General`:
   - Name: `ManagerTaskMonitor`
   - Chon `Run only when user is logged on`
4. Tab `Triggers` -> `New...`:
   - Begin the task: `At log on`
   - Chon user hien tai
5. Tab `Actions` -> `New...`:
   - Action: `Start a program`
   - Program/script: duong dan toi `ManagerTaskMonitor.exe`
   - Start in (optional): thu muc chua file `.exe` va `.env` (nen dien)
6. Tab `Settings`:
   - Cho phep restart neu fail (neu can)
7. `OK` de luu.

Kiem tra task:

- Trong `Task Scheduler Library`, tim `ManagerTaskMonitor`
- Right click -> `Run` de test thu cong
- Xem cot `Last Run Result` de biet thanh cong hay loi.

---

## 5) Cach cap nhat cau hinh sau nay

Khi can doi webhook/nguong:

1. End task `ManagerTaskMonitor.exe` dang chay
2. Sua file `.env`
3. Luu file
4. Chay lai `ManagerTaskMonitor.exe` (hoac `Run` lai task trong Task Scheduler)

Khong can build lai `.exe`.

---

## 6) Mang sang may khac can gi?

Chi can:

- `ManagerTaskMonitor.exe`
- `.env`

Dat cung thu muc tren may moi la chay duoc.

Khong can cai Python.

---

## 7) Xu ly su co nhanh

### Khong thay Discord gui canh bao

- Kiem tra `DISCORD_WEBHOOK_URL` dung hay khong.
- Thu tao webhook moi va thay lai trong `.env`.
- Dam bao `ENABLE_DISCORD_ALERT=true`.
- Dam bao may co internet, khong bi chan Discord.

### Da mo exe nhung khong thay gi

- App chay nen nen khong co cua so la binh thuong.
- Vao Task Manager xem co process `ManagerTaskMonitor.exe` hay khong.

### Doi `.env` nhung app khong nhan

- Ban phai dung process cu va mo lai exe.
- Neu chay qua Task Scheduler, `End` task roi `Run` lai.

### Restart may xong khong tu chay

- Kiem tra task co trigger `At log on` dung user.
- Kiem tra Action tro dung den file `ManagerTaskMonitor.exe`.
- Kiem tra `Start in` trung thu muc chua `.env`.

---

## 8) Khuyen nghi bao mat

- Khong chia se `.env` cho nguoi khong tin cay (vi chua webhook token).
- Neu lo token, vao Discord tao webhook moi va cap nhat lai ngay.

---

## 9) Tom tat quy trinh dung nhanh

1. De `ManagerTaskMonitor.exe` + `.env` cung thu muc.
2. Sua `.env` theo nhu cau.
3. Chay `ManagerTaskMonitor.exe`.
4. Neu muon tu dong khi dang nhap, tao Scheduled Task nhu muc 4.
