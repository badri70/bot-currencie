from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from request import get_exchange_rate


router = Router()


@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет! Я могу предоставить информацию о курсах валют. Используй команду /rate для получения текущих курсов.")


@router.message(Command('rate'))
async def get_rate(message: types.Message):
    rates = get_exchange_rate()
    result = 'Курсы валют:\n'
    for k, v in rates.items():
        result += f"{k}: {v}\n"
    
    await message.answer(result)