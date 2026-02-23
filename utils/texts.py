SEP = "━━━━━━━━━━━━━━━━━━━━━━"


def welcome_new_user(name: str) -> str:
    return f"""🎰 Chào {name}!

{SEP}
✨ <b>SICBO ULTRA PREMIUM</b> ✨
{SEP}

🔥 <b>Vì sao chọn chúng tôi?</b>
• Tỷ lệ thắng minh bạch, công bằng
• Rút tiền nhanh, hỗ trợ 24/7
• Bảo mật tuyệt đối

📜 <b>Cam kết minh bạch</b>
• Kết quả dựa trên Telegram Dice
• Không can thiệp, không gian lận

{SEP}
🎁 <b>THƯỞNG CHÀO MỪNG: 20.000</b>
{SEP}
• Yêu cầu cược: <b>300.000</b> trước khi rút
• Cashback hàng ngày: <b>0.5%</b> tổng cược

👉 Nhấn nút bên dưới để bắt đầu trải nghiệm!"""


def welcome_returning_user(
    name: str,
    balance: str,
    vip_name: str,
    cashback_rate: str,
    withdraw_count_today: int,
    max_withdraw_per_day: int,
) -> str:
    return f"""👋 Chào lại {name}!

{SEP}
📊 <b>DASHBOARD</b>
{SEP}
💰 Số dư: <b>{balance}</b>
🏆 VIP: <b>{vip_name}</b>
💎 Cashback: <b>{cashback_rate}%</b>
📤 Rút hôm nay: <b>{withdraw_count_today}/{max_withdraw_per_day}</b>

{SEP}
👉 Chọn hành động bên dưới."""


def profile_text(
    balance: str,
    total_deposit: str,
    total_withdraw: str,
    total_wager: str,
    profit: str,
    wins: int,
    losses: int,
    win_rate: str,
    cashback_today: str,
    vip_name: str,
    withdraw_today: int,
    max_withdraw: int,
) -> str:
    return f"""👤 <b>HỒ SƠ</b>

{SEP}
💰 Số dư: <b>{balance}</b>
📥 Tổng nạp: {total_deposit}
📤 Tổng rút: {total_withdraw}
🎲 Tổng cược: {total_wager}
{SEP}
📈 Lợi nhuận: <b>{profit}</b>
✅ Thắng: {wins} | ❌ Thua: {losses}
📊 Tỷ lệ thắng: {win_rate}%
{SEP}
💎 Cashback hôm nay: {cashback_today}
🏆 VIP: {vip_name}
📤 Rút hôm nay: {withdraw_today}/{max_withdraw}
{SEP}"""


def help_text() -> str:
    return f"""📖 <b>HƯỚNG DẪN</b>

{SEP}
🎲 <b>Tài Xỉu</b>
• Tài: tổng 3 xúc xắc 11-18
• Xỉu: tổng 3-10
• Cược tối thiểu: 10.000
• Cược tối đa: 1.000.000
• Tỷ lệ: 1.93x (1.87x khi cược max)

💰 <b>Nạp / Rút</b>
• Nạp: tạo mã, chuyển đúng số tiền + nội dung
• Rút: tối thiểu 200.000, tối đa 5 lần/ngày
• Cần hoàn thành yêu cầu cược trước khi rút

🎁 <b>Bonus & Cashback</b>
• Thưởng chào mừng: 20.000
• Yêu cầu cược: 300.000
• Cashback: 0.5% cược trong ngày

📞 <b>Hỗ trợ</b>
• Mở ticket để nhắn với admin (ẩn danh)
• Ticket tự đóng sau 10 phút không hoạt động
{SEP}"""
