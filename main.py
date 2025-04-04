import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import start, register_toilet, find_nearest, feedback, report_problem, rate_toilet, about, admin_panel

# بارگذاری فایل .env
load_dotenv()

# دریافت توکن و آیدی ادمین از محیط
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ثبت هندلرها
dp.include_router(start.router)
dp.include_router(register_toilet.router)
dp.include_router(find_nearest.router)
dp.include_router(feedback.router)
dp.include_router(report_problem.router)
dp.include_router(rate_toilet.router)
dp.include_router(about.router)
dp.include_router(admin_panel.router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
