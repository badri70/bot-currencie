import os
import asyncio
from aiogram import Dispatcher, Bot
from dotenv import load_dotenv
from router import router, scheduler, check_thresholds


load_dotenv()
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()


async def main():
    dp.include_router(router)
    scheduler.add_job(check_thresholds, "interval", minutes=10, args=[bot])
    scheduler.start()
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())