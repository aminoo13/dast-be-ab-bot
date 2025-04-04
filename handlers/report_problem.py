import json
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command

router = Router()
REPORTS_FILE = "storage/reports.json"

# ساخت فایل در صورت نبود
try:
    with open(REPORTS_FILE, "x", encoding="utf-8") as f:
        f.write("[]")
except FileExistsError:
    pass

# تعریف وضعیت‌ها
class ReportState(StatesGroup):
    waiting_for_issue = State()
    waiting_for_custom = State()

# ✅ پشتیبانی از دستور /report یا دکمه "🚫 گزارش مشکل"
@router.message(Command("report"))
@router.message(lambda msg: msg.text == "🚫 گزارش مشکل" or msg.text == "/report")
async def start_report(message: types.Message, state: FSMContext):
    await message.answer(
        "✏️ لطفاً مشکلی که دیدی رو بنویس و بفرست:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ReportState.waiting_for_custom)

# ✅ ذخیره گزارش متنی مستقیم (نه از طریق دکمه خاص دستشویی)
@router.message(ReportState.waiting_for_custom)
async def save_manual_report(message: types.Message, state: FSMContext):
    issue = message.text.strip()
    report = {
        "toilet_id": None,  # چون از طریق دکمه نیومده
        "user_id": message.from_user.id,
        "issue": issue,
        "timestamp": datetime.now().isoformat()
    }

    try:
        with open(REPORTS_FILE, "r", encoding="utf-8") as f:
            reports = json.load(f)
    except json.JSONDecodeError:
        reports = []

    reports.append(report)

    with open(REPORTS_FILE, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)

    await message.answer("✅ گزارش ثبت شد. ممنون از اطلاع‌رسانی 🙌")
    await state.clear()

# ✅ هندل کلیک روی دکمه گزارش خاص برای هر دستشویی
@router.callback_query(F.data.startswith("report:"))
async def report_callback(call: types.CallbackQuery, state: FSMContext):
    toilet_id = int(call.data.split(":")[1])
    await state.update_data(toilet_id=toilet_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 بسته بود", callback_data="issue:بسته بود")],
        [InlineKeyboardButton(text="🛠 خراب بود", callback_data="issue:خراب بود")],
        [InlineKeyboardButton(text="😷 بسیار کثیف", callback_data="issue:بسیار کثیف")],
        [InlineKeyboardButton(text="💧 آب نداشت", callback_data="issue:آب نداشت")],
        [InlineKeyboardButton(text="✏️ نوشتن توضیح دلخواه", callback_data="issue:custom")]
    ])
    await call.message.answer("❗ لطفاً نوع مشکل این دستشویی رو مشخص کن:", reply_markup=keyboard)
    await call.answer()
    await state.set_state(ReportState.waiting_for_issue)

# ✅ انتخاب مشکل از لیست
@router.callback_query(F.data.startswith("issue:"))
async def handle_issue_selection(call: types.CallbackQuery, state: FSMContext):
    issue = call.data.split(":")[1]
    if issue == "custom":
        await call.message.answer("لطفاً توضیح مشکل رو تایپ کن:")
        await state.set_state(ReportState.waiting_for_custom)
    else:
        await save_report(call.from_user, issue, state)
        await call.message.answer("✅ گزارش شما با موفقیت ثبت شد. ممنون از همکاری‌تون 🙏")
        await state.clear()
    await call.answer()

# ✅ ذخیره توضیح دلخواه
@router.message(ReportState.waiting_for_custom)
async def handle_custom_text(message: types.Message, state: FSMContext):
    issue = message.text.strip()
    await save_report(message.from_user, issue, state)
    await message.answer("✅ گزارش با توضیح دلخواه ثبت شد. ممنون از اطلاع‌رسانی 🙌")
    await state.clear()

# ✅ تابع ذخیره گزارش همراه با toilet_id
async def save_report(user, issue, state):
    data = await state.get_data()
    toilet_id = data.get("toilet_id", None)
    report = {
        "toilet_id": toilet_id,
        "user_id": user.id,
        "issue": issue,
        "timestamp": datetime.now().isoformat()
    }

    try:
        with open(REPORTS_FILE, "r", encoding="utf-8") as f:
            reports = json.load(f)
    except json.JSONDecodeError:
        reports = []

    reports.append(report)

    with open(REPORTS_FILE, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)
