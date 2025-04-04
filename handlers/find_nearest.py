
import json
from aiogram import types, Router
from geopy.distance import geodesic
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

router = Router()

# مسیر فایل‌های JSON
DATA_FILE = "storage/toilets.json"
USER_TOILETS_FILE = "storage/user_toilets.json"  # ثبت‌های کاربر

@router.message(Command("find"))
@router.message(lambda message: message.text == "🚀 نزدیک‌ترین دستشویی‌ها به من")
async def request_location(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📍 ارسال موقعیت من", request_location=True)],
            [types.KeyboardButton(text="🔙 بازگشت به منوی اصلی")]
        ],
        resize_keyboard=True
    )
    await message.answer("لطفا موقعیت مکانی خودت رو ارسال کن:", reply_markup=keyboard)


@router.message(lambda message: message.location)
async def handle_location(message: types.Message):
    user_location = (message.location.latitude, message.location.longitude)

    try:
        # 🟢 خواندن داده‌های رسمی از toilets.json
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            # ترکیب همه دسته‌بندی‌ها در یک لیست
            toilets = data["tehran"]["malls"] + data["tehran"]["parks"] + data["tehran"]["mosques"]

        # 🟢 خواندن داده‌های ثبت‌شده توسط کاربران از user_toilets.json
        try:
            with open(USER_TOILETS_FILE, "r", encoding="utf-8") as file:
                user_toilets = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            user_toilets = []

        # 🟢 ترکیب داده‌ها از هر دو فایل
        all_toilets = toilets + user_toilets

        if not all_toilets:
            await message.answer("❌ هیچ دستشویی‌ای در پایگاه داده پیدا نشد.")
            return

        # 🟢 مرتب‌سازی دستشویی‌ها بر اساس فاصله از کاربر
        sorted_toilets = sorted(
            all_toilets,
            key=lambda toilet: geodesic(user_location, (toilet["latitude"], toilet["longitude"])).meters
        )

        # انتخاب ۳ دستشویی نزدیک‌تر
        top_toilets = sorted_toilets[:3]

        for toilet in top_toilets:
            distance = geodesic(user_location, (toilet["latitude"], toilet["longitude"])).meters
            features = toilet.get("features", [])
            features_text = "\n".join(f"• {f}" for f in features) if features else "—"

            # 🟢 محاسبه میانگین امتیازات و آخرین نظر
            ratings = toilet.get("ratings", [])
            if ratings:
                avg_rating = sum(r["score"] for r in ratings) / len(ratings)
                last_comment = ratings[-1]["comment"]
                stars = "⭐" * round(avg_rating) + "☆" * (5 - round(avg_rating))
                rating_text = f"{stars} ({len(ratings)} نظر) - آخرین نظر: \"{last_comment}\""
            else:
                rating_text = "⭐ هنوز نظری ثبت نشده است."

            # 🟢 مشخص کردن نوع دستشویی
            toilet_type = toilet.get("type", "نامشخص")
            type_text = {
                "mall": "🏬 مرکز خرید",
                "park": "🌳 بوستان",
                "mosque": "🕌 مسجد",
                "user": "✏️ ثبت‌شده توسط کاربر"
            }.get(toilet_type, "❗️ نامشخص")

            # متن پیام
            caption = (
                f"✅ دستشویی نزدیک:\n"
                f"📍 آدرس: {toilet['address']}\n"
                f"📏 فاصله: {int(distance)} متر\n"
                f"🏷 نوع مکان: {type_text}\n"
                f"🧰 امکانات:\n{features_text}\n\n"
                f"💬 امتیاز: {rating_text}"
            )

            # لینک مسیریابی در گوگل مپ
            maps_link = f"https://www.google.com/maps/search/?api=1&query={toilet['latitude']},{toilet['longitude']}"

            # دکمه‌ها
            inline_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🗺 مسیریابی در گوگل مپ", url=maps_link)],
                [
                    InlineKeyboardButton(text="🚫 گزارش مشکل", callback_data=f"report:{toilet['id']}"),
                    InlineKeyboardButton(text="⭐ ثبت امتیاز", callback_data=f"rate:{toilet['id']}")
                ]
            ])

            # نمایش عکس دستشویی (در صورت وجود)
            photo = toilet.get("photo_file_id")
            if photo:
                await message.bot.send_photo(
                    chat_id=message.chat.id,
                    photo=photo,
                    caption=caption,
                    reply_markup=inline_kb,
                    parse_mode="Markdown"
                )
            else:
                await message.answer(
                    text=caption,
                    reply_markup=inline_kb,
                    parse_mode="Markdown"
                )

    except Exception as e:
        await message.answer(f"❌ مشکلی پیش اومد! خطا: {e}")
