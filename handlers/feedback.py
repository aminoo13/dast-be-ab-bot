from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove
import json
from pathlib import Path
from datetime import datetime
from aiogram.filters import Command

# مسیر فایل نظرات
FEEDBACK_FILE = Path("storage/feedbacks.json")

# اگر فایل وجود نداشت، یه آرایه خالی بساز
if not FEEDBACK_FILE.exists():
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    FEEDBACK_FILE.write_text("[]", encoding="utf-8")

# ساختار وضعیت‌ها برای دریافت نظر
class FeedbackState(StatesGroup):
    waiting_for_feedback = State()

router = Router()

# ✅ هندل دکمه یا دستور /feedback
@router.message(Command("feedback"))
@router.message(lambda msg: msg.text == "💬 ارسال نظر یا پیشنهاد" or msg.text == "/feedback")
async def ask_feedback(message: Message, state: FSMContext):
    await message.answer(
        "لطفاً نظر یا پیشنهادت رو تایپ کن و بفرست:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(FeedbackState.waiting_for_feedback)

# ✅ ذخیره نظر در فایل
@router.message(FeedbackState.waiting_for_feedback)
async def save_feedback(message: Message, state: FSMContext):
    feedback_text = message.text.strip()
    if not feedback_text:
        await message.answer("⚠️ لطفاً یک متن معتبر وارد کن.")
        return

    # بارگذاری نظرات قبلی
    try:
        with FEEDBACK_FILE.open("r", encoding="utf-8") as f:
            feedbacks = json.load(f)
    except json.JSONDecodeError:
        feedbacks = []

    # ذخیره نظر جدید
    feedbacks.append({
        "user_id": message.from_user.id,
        "first_name": message.from_user.first_name,
        "text": feedback_text,
        "date": datetime.now().isoformat()
    })

    with FEEDBACK_FILE.open("w", encoding="utf-8") as f:
        json.dump(feedbacks, f, indent=2, ensure_ascii=False)

    await message.answer("✅ نظر یا پیشنهادت با موفقیت ثبت شد. ممنون از مشارکتت 🙏")
    await state.clear()
