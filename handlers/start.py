from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
       keyboard=[
            [KeyboardButton(text="🚀 نزدیک‌ترین دستشویی‌ها به من")],
            [KeyboardButton(text="➕ ثبت دستشویی جدید"), KeyboardButton(text="💬 ارسال نظر یا پیشنهاد")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "🧻 به ربات پیدا کردن دستشویی خوش اومدی!\n"
        "یه همراه دم‌دستی برای لحظه‌های حساس 😅\n\n"
        "🔍 اگه دنبال دستشویی نزدیکت هستی، کافیه بزنی روی /find و موقعیتت رو بفرستی تا سریـع‌ترین راهو نشونت بده!\n\n"
        "➕ یه دستشویی خوب دیدی و می‌خوای برای بقیه هم ثبتش کنی؟ بزن روی /register و جزئیاتش رو وارد کن 🚽\n\n"
        "💬 پیشنهاد، انتقاد یا حرفی با ما داری؟ خوشحال می‌شیم ازت بشنویم! اینجا بزن → /feedback 📢\n\n"
        "🚫 اگه یه دستشویی بسته بود یا مشکلی داشت، با /report خبر بده تا بررسیش کنیم.\n\n"
        "ℹ️ برای آشنایی بیشتر با ربات و هدفش هم می‌تونی بزنی روی /about\n\n"
        "👇 از منوی پایین هم می‌تونی سریع به گزینه‌ها دسترسی داشته باشی!",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
