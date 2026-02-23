from config import settings
from utils.formatters import format_currency

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


def welcome_new_user(name: str) -> str:
    bonus = format_currency(settings.WELCOME_BONUS)
    wager = format_currency(settings.WAGER_REQUIREMENT)
    cb = f"{settings.CASHBACK_RATE * 100:.1f}".rstrip("0").rstrip(".")
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
🎁 <b>THƯỞNG CHÀO MỪNG: {bonus}</b>
{SEP}
• Yêu cầu cược: <b>{wager}</b> trước khi rút
• Cashback hàng ngày: <b>{cb}%</b> tổng cược

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
    min_bet = format_currency(settings.MIN_BET)
    max_bet = format_currency(settings.MAX_BET)
    min_wd = format_currency(settings.MIN_WITHDRAW)
    bonus = format_currency(settings.WELCOME_BONUS)
    wager = format_currency(settings.WAGER_REQUIREMENT)
    cb = f"{settings.CASHBACK_RATE * 100:.1f}".rstrip("0").rstrip(".")
    return f"""📖 <b>HƯỚNG DẪN</b>

{SEP}
🎲 <b>Tài Xỉu</b>
• Tài: tổng 3 xúc xắc {settings.TAI_MIN}-{settings.TAI_MAX}
• Xỉu: tổng 3-10
• Cược tối thiểu: {min_bet}
• Cược tối đa: {max_bet}
• Tỷ lệ: {settings.PAYOUT_NORMAL}x ({settings.PAYOUT_MAX_BET}x khi cược max)

💰 <b>Nạp / Rút</b>
• Nạp: tạo mã, chuyển đúng số tiền + nội dung
• Rút: tối thiểu {min_wd}, tối đa {settings.MAX_WITHDRAW_PER_DAY} lần/ngày
• Cần hoàn thành yêu cầu cược trước khi rút

🎁 <b>Bonus & Cashback</b>
• Thưởng chào mừng: {bonus}
• Yêu cầu cược: {wager}
• Cashback: {cb}% cược trong ngày

📞 <b>Hỗ trợ</b>
• Mở ticket để nhắn với admin (ẩn danh)
• Ticket tự đóng sau {settings.TICKET_INACTIVITY_MINUTES} phút không hoạt động
{SEP}"""
