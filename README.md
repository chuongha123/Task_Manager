# Task Manager

Script Python nho de tim kiem va loc cac tien trinh dang chay tren may bang `psutil`.

## Tinh nang

- Loc theo ten tien trinh (`ten_chua`)
- Loc theo nguong CPU toi thieu (`cpu_min`)
- Loc theo nguong RAM toi thieu (`ram_min`)
- Bo qua cac tien trinh khong the truy cap hoac da ket thuc

## Cai dat

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Chay chuong trinh

```bash
python Task_Manager.py
```

## Ghi chu ve moi truong

Neu gap loi `ModuleNotFoundError: No module named 'psutil'`, hay dam bao:

- Ban da `source venv/bin/activate`
- Hoac chay truc tiep dung interpreter:

```bash
venv/bin/python Task_Manager.py
```

