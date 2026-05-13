## Yêu Cầu

- Python 3.7+
- Pygame 2.5.0 trở lên

## Cài Đặt

1. Clone repository này:
```bash
git clone <repository-url>
cd TriTueNhanTao
```

2. Tạo môi trường ảo (tùy chọn nhưng được khuyên dùng):
```bash
python -m venv .venv
```

3. Kích hoạt môi trường ảo:
   - Trên Windows:
   ```bash
   .venv\Scripts\activate
   ```
   - Trên macOS/Linux:
   ```bash
   source .venv/bin/activate
   ```

4. Cài đặt các phụ thuộc:
```bash
pip install -r requirement.txt
```

## Cách Chạy

Từ thư mục gốc, chạy lệnh:

```bash
python source_code/main.py
```

## Cấu Trúc Dự Án

```
TriTueNhanTao/
├── README.md              # Tệp hướng dẫn này
├── requirement.txt        # Danh sách các thư viện cần cài đặt
├── reports/              # Thư mục chứa báo cáo
└── source_code/
    ├── main.py           # Điểm vào chính của ứng dụng
    ├── game.py           # Lớp quản lý trò chơi chính
    ├── board.py          # Lớp quản lý bàn cờ
    ├── ai.py             # Lớp trí tuệ nhân tạo
    ├── gui.py            # Giao diện người dùng
    └── constants.py      # Các hằng số toàn cục
```

## Luật Chơi

Caro là một trò chơi tranh tài giữa hai người chơi trên một bàn cờ:
- Mục tiêu là nối được 5 quân cờ liên tiếp (theo chiều ngang, dọc hoặc chéo)
- Người chơi lần lượt đặt quân cờ của mình lên bàn cờ
- Người chơi đầu tiên nối được 5 quân liên tiếp là người thắng

## Tác Giả

Dự án này được thực hiện bởi:
- 24020268 Nguyễn Chí Phong
- 23020109 Vũ Văn Mạnh
- 23021204 Đỗ Thành An

## Ghi Chú

- Bàn cờ mặc định là 15x15
- Độ sâu tìm kiếm AI có thể điều chỉnh để thay đổi độ khó
