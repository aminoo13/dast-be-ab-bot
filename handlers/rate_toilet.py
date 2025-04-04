import json
from datetime import datetime, timedelta
from aiogram import Router, types, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

RATINGS_FILE = "storage/ratings.json"
SHOWN_TOILETS_FILE = "storage/shown_toilets.json"

# ساخت فایل اولیه اگر وجود نداشت
for file_path in [RATINGS_FILE, SHOWN_TOILETS_FILE]:
    try:
        with open(file_path, "x", encoding="utf-8") as f:
            f.write("[]")
    except FileExistsError:
        pass

class RatingState(StatesGroup):
    waiting_for_score = State()

@router.callback_query(F.data.startswith("rate:"))
async def handle_rating_callback(call: types.CallbackQuery, state: FSMContext):
    toilet_id = int(call.data.split(":")[1])
    user_id = call.from_user.id

    # بررسی اینکه این کاربر این دستشویی رو کی دیده
    with open(SHOWN_TOILETS_FILE, "r", encoding="utf-8") as f:
        shown_data = json.load(f)

    record = next(
        (item for item in shown_data if item["user_id"] == user_id and item["toilet_id"] == toilet_id),
        None
    )

    if not record:
        await call.message.answer("⚠️ ابتدا باید این دستشویی رو مشاهده کرده باشی.")
        await call.answer()
        return

    shown_time = datetime.fromisoformat(record["shown_at"])
    now = datetime.now()

    if now - shown_time < timedelta(minutes=5):
        await call.message.answer("⏳ لطفاً بعد از استفاده از دستشویی (حداقل ۵ دقیقه بعد) امتیاز بده.")
        await call.answer()
        return

    await state.update_data(toilet_id=toilet_id)
    await call.message.answer(
        "لطفاً امتیاز خودت رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⭐ خیلی بد", callback_data="score:1")],
            [InlineKeyboardButton(text="⭐⭐ بد", callback_data="score:2")],
            [InlineKeyboardButton(text="⭐⭐⭐ متوسط", callback_data="score:3")],
            [InlineKeyboardButton(text="⭐⭐⭐⭐ خوب", callback_data="score:4")],
            [InlineKeyboardButton(text="⭐⭐⭐⭐⭐ عالی", callback_data="score:5")],
        ])
    )
    await call.answer()
    await state.set_state(RatingState.waiting_for_score)

@router.callback_query(RatingState.waiting_for_score, F.data.startswith("score:"))
async def save_rating(call: types.CallbackQuery, state: FSMContext):
    score = int(call.data.split(":")[1])
    data = await state.get_data()
    toilet_id = data["toilet_id"]

    rating = {
        "toilet_id": toilet_id,
        "user_id": call.from_user.id,
        "score": score,
        "timestamp": datetime.now().isoformat()
    }

    with open(RATINGS_FILE, "r+", encoding="utf-8") as f:
        ratings = json.load(f)
        ratings.append(rating)
        f.seek(0)
        json.dump(ratings, f, indent=2, ensure_ascii=False)

    await call.message.answer(f"✅ امتیاز شما ثبت شد. ممنون از مشارکتتون! ⭐️ امتیاز: {score}")
    await state.clear()
    await call.answer()
