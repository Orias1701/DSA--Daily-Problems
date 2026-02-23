# Telegram Casino Bot – SICBO ULTRA PREMIUM

Bot Telegram Tài Xỉu production-ready với aiogram 3, SQLite/PostgreSQL, bonus, cashback, VIP, nạp/rút, support ticket và admin panel.

**Open source** – chạy được trên Windows, macOS và Linux.

## Cấu trúc thư mục

```
PY--Teletool/
├── config/           # Cấu hình (settings)
├── database/        # Models, engine, repositories
├── handlers/        # Start, game, deposit, withdraw, profile, support, admin, coupon
├── keyboards/       # Inline keyboards
├── middlewares/     # DB session, ban check
├── services/        # Game logic, Bank API
├── states/          # FSM states
├── utils/           # Formatters, texts
├── main.py          # Entry point
├── setup_venv.py    # Script setup venv (cross-platform)
├── setup.bat        # Setup nhanh trên Windows (double-click)
├── setup.sh         # Setup nhanh trên macOS / Linux
├── requirements.txt
└── .env.example
```

## Cài đặt

Cần **Python 3.10+** đã cài và có trong `PATH`.

### Cách 1: Dùng script setup (khuyến nghị)

| Hệ điều hành | Lệnh / Thao tác |
|--------------|------------------|
| **Windows**  | Double-click `setup.bat` hoặc chạy `python setup_venv.py` |
| **macOS / Linux** | `chmod +x setup.sh && ./setup.sh` hoặc `python3 setup_venv.py` |

Script sẽ tạo `.venv` và cài đặt dependencies từ `requirements.txt`.

### Cách 2: Tự gõ lệnh

**Windows (PowerShell / CMD):**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Sau khi cài xong

1. Copy file cấu hình: `cp .env.example .env` (trên Mac/Linux) hoặc copy `.env.example` thành `.env` (Windows).
2. Sửa `.env`: điền `BOT_TOKEN`, `ADMIN_IDS` (ID Telegram của admin, cách nhau bằng dấu phẩy).

## Chạy bot

**Windows:** (sau khi đã chạy setup)
```bash
.venv\Scripts\activate
python main.py
```

**macOS / Linux:**
```bash
source .venv/bin/activate
python main.py
```

---

## Hướng dẫn sử dụng

### Windows

1. **Cài Python**  
   Tải [python.org](https://www.python.org/downloads/) (3.10 trở lên). Khi cài, chọn **“Add Python to PATH”**.

2. **Mở thư mục dự án**  
   Mở Command Prompt hoặc PowerShell, chạy:
   ```cmd
   cd đường\dẫn\tới\PY--Teletool
   ```

3. **Setup môi trường ảo**  
   - **Cách nhanh:** Double-click file `setup.bat` trong thư mục dự án.  
   - **Hoặc gõ lệnh:**
     ```cmd
     python setup_venv.py
     ```

4. **Tạo file cấu hình**  
   - Copy file `.env.example` và đổi tên thành `.env` (cùng thư mục).  
   - Mở `.env` bằng Notepad hoặc editor, sửa:
     - `BOT_TOKEN=` → dán token từ [@BotFather](https://t.me/BotFather).
     - `ADMIN_IDS=` → điền ID Telegram của bạn (ví dụ: `123456789`). Nhiều admin thì cách nhau bằng dấu phẩy.

5. **Chạy bot**  
   Trong Command Prompt / PowerShell (cùng thư mục dự án):
   ```cmd
   .venv\Scripts\activate
   python main.py
   ```
   Thấy dòng “Bot started.” là bot đã chạy. Mở Telegram, tìm bot của bạn và gửi `/start`.

6. **Lần sau muốn chạy lại**  
   Mở CMD/PowerShell → `cd` vào thư mục dự án → chạy:
   ```cmd
   .venv\Scripts\activate
   python main.py
   ```

---

### MacBook (macOS)

1. **Cài Python**  
   Mac thường có sẵn Python. Kiểm tra:
   ```bash
   python3 --version
   ```
   Nếu chưa có hoặc phiên bản < 3.10, cài qua [python.org](https://www.python.org/downloads/) hoặc Homebrew:
   ```bash
   brew install python@3.11
   ```

2. **Mở thư mục dự án**  
   Mở Terminal, chạy:
   ```bash
   cd /đường/dẫn/tới/PY--Teletool
   ```

3. **Setup môi trường ảo**  
   - **Cách nhanh:** Chạy script setup:
     ```bash
     chmod +x setup.sh
     ./setup.sh
     ```
   - **Hoặc dùng trực tiếp Python:**
     ```bash
     python3 setup_venv.py
     ```

4. **Tạo file cấu hình**  
   ```bash
   cp .env.example .env
   ```
   Mở `.env` (TextEdit, VS Code, v.v.), sửa:
   - `BOT_TOKEN=` → dán token từ [@BotFather](https://t.me/BotFather).
   - `ADMIN_IDS=` → điền ID Telegram của bạn (ví dụ: `123456789`). Nhiều admin thì cách nhau bằng dấu phẩy.

5. **Chạy bot**  
   Trong Terminal:
   ```bash
   source .venv/bin/activate
   python main.py
   ```
   Thấy “Bot started.” là bot đã chạy. Mở Telegram, tìm bot và gửi `/start`.

6. **Lần sau muốn chạy lại**  
   Mở Terminal → `cd` vào thư mục dự án → chạy:
   ```bash
   source .venv/bin/activate
   python main.py
   ```

---

## Tính năng

- **/start**: New user → onboarding + 20k bonus; Returning → dashboard (số dư, VIP, cashback, lượt rút).
- **Tài Xỉu**: Cược Tài (11–18) / Xỉu (3–10), dùng Telegram Dice 🎲, min 10k / max 1M, tỷ lệ 1.93x (1.87x khi cược max).
- **Bonus**: 20k cho user mới; yêu cầu cược 300k trước khi rút.
- **Cashback**: 0.5% tổng cược trong ngày, reset theo ngày.
- **VIP**: Cấp theo tổng cược, hiển thị trong profile.
- **Nạp**: Mã NAP + 6 ký tự, hướng dẫn chuyển khoản; có thể tích hợp Bank API để tự duyệt.
- **Rút**: Min 200k, tối đa 5 lần/ngày, phải đủ yêu cầu cược; admin duyệt/từ chối.
- **Profile**: Số dư, tổng nạp/rút/cược, lợi nhuận, thắng/thua, win rate, cashback, VIP, lượt rút; /help.
- **Support**: Ticket ẩn danh; tự đóng sau 10 phút không hoạt động.
- **Admin (/admin)**: Chỉ ADMIN_IDS. Duyệt/từ chối nạp-rút, broadcast, listusers, check user, show_bets, create/delete/couponinfo, maintenance, ban/unban, profit/today/weekly.

## Biến môi trường (.env)

**Tất cả chỉ số cấu hình (giá cả, tên chủ TK, giới hạn…) đều đặt biến trong `.env` và có thể thay đổi mà không cần sửa code.**

| Biến | Mô tả | Mặc định |
|------|--------|----------|
| `BOT_TOKEN` | Token bot từ @BotFather | (bắt buộc) |
| `ADMIN_IDS` | ID Telegram admin, cách nhau dấu phẩy | (bắt buộc) |
| `DATABASE_URL` | SQLite hoặc PostgreSQL | `sqlite+aiosqlite:///./data/bot.db` |
| `BANK_API_ENABLED`, `BANK_API_URL` | Bật và URL API ngân hàng (tự duyệt nạp) | `false`, rỗng |
| **Ngân hàng nhận tiền** | | |
| `ADMIN_BANK_NAME` | Tên ngân hàng | Ngân hàng TMCP |
| `ADMIN_BANK_NUMBER` | Số tài khoản | 1234567890 |
| `ADMIN_BANK_HOLDER` | Tên chủ tài khoản | CONG TY SICBO |
| `ADMIN_BANK_BIN` | BIN ngân hàng (VietQR) | rỗng |
| `VIETQR_TEMPLATE` | Template ảnh VietQR | compact2 |
| **Game Tài Xỉu** | | |
| `MIN_BET`, `MAX_BET` | Cược min/max (VNĐ) | 10000, 1000000 |
| `PAYOUT_NORMAL`, `PAYOUT_MAX_BET` | Tỷ lệ thắng | 1.93, 1.87 |
| `TAI_MIN`, `TAI_MAX` | Khoảng Tài (tổng xúc xắc) | 11, 18 |
| `BET_AMOUNT_PRESETS` | Mức cược trên nút, cách nhau dấu phẩy | 10000,50000,... |
| **Bonus & Cashback** | | |
| `WELCOME_BONUS` | Thưởng chào mừng (VNĐ) | 20000 |
| `WAGER_REQUIREMENT` | Yêu cầu cược trước khi rút (VNĐ) | 300000 |
| `CASHBACK_RATE` | Tỷ lệ cashback (số thập phân) | 0.005 |
| **Nạp / Rút** | | |
| `MIN_DEPOSIT` | Nạp tối thiểu (VNĐ) | 10000 |
| `MIN_WITHDRAW` | Rút tối thiểu (VNĐ) | 200000 |
| `MAX_WITHDRAW_PER_DAY` | Số lần rút tối đa mỗi ngày | 5 |
| **Hệ thống** | | |
| `TICKET_INACTIVITY_MINUTES` | Tự đóng ticket sau (phút) | 10 |
| `DAILY_RESET_HOUR` | Giờ reset hàng ngày (UTC) | 0 |

Chi tiết đầy đủ xem file `.env.example`.

## Database

SQLite tạo file tại `./data/bot.db`. Các bảng: users, transactions, bets, vip_levels, coupons, coupon_uses, tickets, ticket_messages, admin_logs. VIP mặc định được seed khi khởi động.
