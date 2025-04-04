import json
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Message
from aiogram.filters import Command

router = Router()

# مسیر ذخیره فایل‌ها
DATA_FILE = "storage/toilets.json"  # داده‌های رسمی
USER_TOILETS_FILE = "storage/user_toilets.json"  # داده‌های ثبت‌شده توسط کاربران

# تعریف Stateها برای مدیریت مراحل ثبت دستشویی
class RegisterToilet(StatesGroup):
    waiting_for_location = State()
    waiting_for_features = State()
    waiting_for_photo = State()
    waiting_for_address = State()

# دکمه‌های امکانات دستشویی
features_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚻 تمیز بودن"), KeyboardButton(text="💧 آب دستشویی دارد")],
        [KeyboardButton(text="🧻 دستمال دارد"), KeyboardButton(text="🧼 صابون دارد")],
        [KeyboardButton(text="♿ مناسب افراد معلول"), KeyboardButton(text="💡 روشنایی خوب")],
        [KeyboardButton(text="🆓 رایگان است")],
        [KeyboardButton(text="✅ ادامه ثبت")]
    ],
    resize_keyboard=True
)

# آماده‌سازی فایل user_toilets.json اگر وجود نداشت
try:
    with open(USER_TOILETS_FILE, "x", encoding="utf-8") as f:
        f.write("[]")
except FileExistsError:
    pass

@router.message(Command("register"))
@router.message(lambda message: message.text == "➕ ثبت دستشویی جدید")
async def start_register_toilet(message: types.Message, state: FSMContext):
    await message.answer("📍 لطفا موقعیت دستشویی رو ارسال کن:")
    await state.set_state(RegisterToilet.waiting_for_location)

@router.message(RegisterToilet.waiting_for_location)
async def save_toilet_location(message: types.Message, state: FSMContext):
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude

        await state.update_data(latitude=latitude, longitude=longitude, features=[])
        await message.answer("🏷 لطفاً امکانات دستشویی رو انتخاب کن. بعد از انتخاب دکمه‌ها، روی «✅ ادامه ثبت» بزن.", reply_markup=features_keyboard)
        await state.set_state(RegisterToilet.waiting_for_features)
    else:
        await message.answer("❗️ موقعیت معتبر ارسال کن!")

@router.message(RegisterToilet.waiting_for_features)
async def select_features(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    selected = data.get("features", [])

    if text == "✅ ادامه ثبت":
        await message.answer("📸 لطفاً یک عکس از این دستشویی ارسال کن:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(RegisterToilet.waiting_for_photo)
        return

    if text not in selected:
        selected.append(text)
        await state.update_data(features=selected)
        await message.answer(f"✅ افزوده شد: {text}")
    else:
        await message.answer("⚠️ این گزینه قبلاً انتخاب شده.")

@router.message(RegisterToilet.waiting_for_photo, F.photo)
async def save_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data(photo_file_id=photo.file_id)
    await message.answer("🏢 حالا آدرس یا توضیحاتی درباره این دستشویی بنویس:")
    await state.set_state(RegisterToilet.waiting_for_address)

@router.message(RegisterToilet.waiting_for_address)
async def save_toilet_address(message: types.Message, state: FSMContext):
    data = await state.get_data()
    latitude = data["latitude"]
    longitude = data["longitude"]
    features = data.get("features", [])
    photo_file_id = data.get("photo_file_id")
    address = message.text

    try:
        with open(USER_TOILETS_FILE, "r", encoding="utf-8") as file:
            user_toilets = json.load(file)

        new_toilet = {
            "id": len(user_toilets) + 1,
            "latitude": latitude,
            "longitude": longitude,
            "features": features,
            "photo_file_id": photo_file_id,
            "address": address
        }
        user_toilets.append(new_toilet)

        with open(USER_TOILETS_FILE, "w", encoding="utf-8") as file:
            json.dump(user_toilets, file, ensure_ascii=False, indent=2)

        await message.answer_photo(
            photo_file_id,
            caption=(
                f"✅ دستشویی ثبت شد!\n"
                f"📍 آدرس: {address}\n"
                f"🧰 امکانات:\n" +
                "\n".join(f"• {feature}" for feature in features)
            )
        )
        await state.clear()

    except Exception as e:
        await message.answer(f"❌ مشکلی در ثبت دستشویی پیش اومد! خطا: {e}")