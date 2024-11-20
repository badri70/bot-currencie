from aiogram import Router, types, Bot
from aiogram.filters import Command, CommandStart
from request import get_exchange_rate
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler


router = Router()
scheduler = AsyncIOScheduler()
user_thresholds = {}

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Вывести курс популярных валют")],
        [KeyboardButton(text="Установить порог для отслеживания курса")],
        [KeyboardButton(text="Выбрать валюту")],
        [KeyboardButton(text="Помощь")]
    ],
    resize_keyboard=True
)


class CurrencieState(StatesGroup):
    currency = State()
    threshold = State()


@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет! Я могу предоставить информацию о курсах валют. Используй команду /rate для получения текущих курсов.", reply_markup=keyboard)


@router.message(lambda message: message.text == "Вывести курс популярных валют" or message.text == "/rate")
async def get_rate(message: types.Message):
    rates = get_exchange_rate()
    result = 'Курсы популярных валют:\n'
    selected_currencies = ["EUR", "GBP", "JPY", "RUB"]
    for currency in selected_currencies:
        result += f"{currency}: {round(rates.get(currency, 'нет данных'), 2)}\n"
    
    await message.answer(result)


@router.message(lambda message: message.text == "Установить порог для отслеживания курса")
async def set_threshold_step1(message: types.Message, state: FSMContext):
    await message.answer("Введите код валюты, например, EUR:")
    await state.set_state(CurrencieState.currency)


@router.message(CurrencieState.currency)
async def set_threshold_step2(message: types.Message, state: FSMContext):
    await state.update_data(currency=message.text.upper())
    await message.answer("Теперь введите пороговое значение:")
    await state.set_state(CurrencieState.threshold)


@router.message(CurrencieState.threshold)
async def set_threshold_step3(message: types.Message, state: FSMContext):
    try:
        threshold = float(message.text)
        user_data = await state.get_data()
        currency = user_data["currency"]
        user_id = message.from_user.id

        if user_id not in user_thresholds:
            user_thresholds[user_id] = {}
        user_thresholds[user_id][currency] = threshold

        await message.answer(f"Порог для {currency} установлен на {threshold}.")
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение.")


async def check_thresholds(bot: Bot):
    rates = get_exchange_rate()
    for user_id, thresholds in user_thresholds.items():
        for currency, threshold in thresholds.items():
            current_rate = rates.get(currency)
            if current_rate and current_rate < threshold:
                await bot.send_message(user_id, f"⚠️ Курс {currency} упал ниже {threshold}: сейчас {round(current_rate, 2)}")


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
    await callback_query.message.edit_text(f"Курс {currency}: {round(rate, 2)}")


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