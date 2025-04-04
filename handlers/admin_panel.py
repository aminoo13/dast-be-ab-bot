from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
from pathlib import Path

router = Router()
ADMIN_ID = 393403801  # فقط ادمین!

# مسیر فایل‌ها
FEEDBACK_FILE = Path("storage/feedbacks.json")
REPORT_FILE = Path("storage/reports.json")
USER_TOILETS_FILE = Path("storage/user_toilets.json")

# ➤ شروع پنل ادمین
@router.message(Command("admin"))
async def admin_entry(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ شما به پنل ادمین دسترسی ندارید.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 آمار کلی", callback_data="admin:stats")],
        [InlineKeyboardButton(text="🧾 بازخوردها", callback_data="admin:feedbacks")],
        [InlineKeyboardButton(text="🚫 گزارش‌ها", callback_data="admin:reports")],
        [InlineKeyboardButton(text="📍 دستشویی‌های کاربران", callback_data="admin:toilets")],
        [InlineKeyboardButton(text="🔙 خروج", callback_data="admin:exit")]
    ])
    await message.answer("👑 به پنل ادمین خوش اومدی. لطفاً یکی از گزینه‌ها رو انتخاب کن:", reply_markup=keyboard)


# ➤ هندلر دکمه‌های پنل
@router.callback_query(F.data.startswith("admin:"))
async def handle_admin_actions(call: types.CallbackQuery):
    action = call.data.split(":")[1]

    if call.from_user.id != ADMIN_ID:
        await call.answer("⛔ شما ادمین نیستید.", show_alert=True)
        return

    if action == "exit":
        await call.message.edit_text("❌ از پنل ادمین خارج شدی.")
        return

    elif action == "stats":
        feedbacks = json.loads(FEEDBACK_FILE.read_text(encoding="utf-8")) if FEEDBACK_FILE.exists() else []
        reports = json.loads(REPORT_FILE.read_text(encoding="utf-8")) if REPORT_FILE.exists() else []
        toilets = json.loads(USER_TOILETS_FILE.read_text(encoding="utf-8")) if USER_TOILETS_FILE.exists() else []

        # فقط آیتم‌هایی که user_id دارند را بشمار
        user_ids = {t["user_id"] for t in toilets if "user_id" in t}

        text = (
            f"📊 آمار کلی:\n"
            f"👥 کاربران ثبت‌کننده دستشویی: {len(user_ids)}\n"
            f"📍 مجموع دستشویی‌های ثبت‌شده توسط کاربران: {len(toilets)}\n"
            f"🧾 نظرات: {len(feedbacks)}\n"
            f"🚫 گزارش مشکلات: {len(reports)}"
        )
        await call.message.edit_text(text)


    elif action == "feedbacks":
        feedbacks = json.loads(FEEDBACK_FILE.read_text(encoding="utf-8")) if FEEDBACK_FILE.exists() else []
        if not feedbacks:
            await call.message.edit_text("❗ هنوز نظری ثبت نشده.")
            return

        recent = feedbacks[-5:]  # آخرین ۵ مورد
        text = "🗣 بازخوردها:\n\n" + "\n".join(
    f"👤 {f.get('first_name', 'ناشناس')}\n📝 {f.get('text', '---')}" for f in reversed(recent)
)

        await call.message.edit_text(text)

    elif action == "reports":
        reports = json.loads(REPORT_FILE.read_text(encoding="utf-8")) if REPORT_FILE.exists() else []
        if not reports:
            await call.message.edit_text("❗ گزارشی ثبت نشده.")
            return

        recent = reports[-5:]
        text = "🚫 آخرین گزارش‌ها:\n\n" + "\n\n".join(
            f"🆔 ID دستشویی: {r['toilet_id']}\n📝 {r['issue']}" for r in reversed(recent)
        )
        await call.message.edit_text(text)

    elif action == "toilets":
        toilets = json.loads(USER_TOILETS_FILE.read_text(encoding="utf-8")) if USER_TOILETS_FILE.exists() else []
        if not toilets:
            await call.message.edit_text("📍 هیچ دستشویی توسط کاربر ثبت نشده.")
            return

        recent = toilets[-3:]
        text = "📍 آخرین دستشویی‌های ثبت‌شده:\n\n" + "\n\n".join(
            f"🗺 {t['address']}" for t in reversed(recent)
        )
        await call.message.edit_text(text)

    await call.answer()
