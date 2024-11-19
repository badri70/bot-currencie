from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from request import get_exchange_rate
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


router = Router()


keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Выбрать валюту")],
        [KeyboardButton(text="Помощь")]
    ],
    resize_keyboard=True
)


@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет! Я могу предоставить информацию о курсах валют. Используй команду /rate для получения текущих курсов.", reply_markup=keyboard)


@router.message(Command('rate'))
async def get_rate(message: types.Message):
    rates = get_exchange_rate()
    result = 'Курсы популярных валют:\n'
    selected_currencies = ["EUR", "GBP", "JPY", "RUB"]
    for currency in selected_currencies:
        result += f"{currency}: {rates.get(currency, 'нет данных')}\n"
    
    await message.answer(result)


async def inline_button_handler():
    selected_currencies = ["EUR", "GBP", "JPY", "RUB"]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=currency, callback_data=f"rate:{currency}")]
            for currency in selected_currencies
        ]
    )


@router.message(lambda message: message.text == "Выбрать валюту")
async def which_currencie(message: types.Message):
    keyboard_inline = await inline_button_handler()
    if keyboard_inline:
        await message.answer("Выберите валюту для получения курса:", reply_markup=keyboard_inline)
    else:
        await message.answer("Что-то пошло не так. Повторите попытку позже.")


@router.callback_query(lambda call: call.data.startswith("rate:"))
async def get_currencie(callback_query: types.CallbackQuery):
    currency = callback_query.data.split(":")[1]
    rates = get_exchange_rate()
    rate = rates.get(currency, "Неизвестная валюта")
    await callback_query.message.edit_text(f"Курс {currency}: {rate}")


@router.message(lambda message: message.text == "Помощь" or message.text == "/help")
async def help(message: types.Message):
    help_text = (
        "🔹 **Добро пожаловать!**\n\n"
        "Я бот, который поможет вам узнать актуальные курсы валют и сделать взаимодействие с финансовой информацией удобным.\n\n"
        "📋 Вот список доступных команд:\n"
        " - **/start** — Запустить бота и получить приветственное сообщение.\n"
        " - **/help** — Показать это меню с описанием доступных функций.\n"
        " - **/rate** — Получить список текущих курсов валют.\n"
        " - **/which** — Выбрать конкретную валюту для получения курса.\n\n"
        "❓ Если у вас есть предложения или вопросы, просто напишите мне! 🚀"
    )
    await message.answer(help_text, parse_mode="Markdown")