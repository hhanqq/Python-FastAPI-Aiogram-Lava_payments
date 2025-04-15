from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from fastapi import FastAPI, Request
import logging
import requests
import asyncio
import uvicorn
import keybords as kb

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
API_TOKEN = '7691943629:AAGE6UxFcZucZc0xWbwpQMVwNzpQyeG-i2I'
LAVA_API_URL = 'https://gate.lava.top/api/v2'
LAVA_API_KEY = 'bKoAyqhc4J9IciJ81NmDUibgk99nDH6aUYw4pAQsvgBU2W1BMVD4aclpMOA5Onn8'

# Используем DefaultBotProperties для настройки parse_mode
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # Указываем parse_mode здесь
)
dp = Dispatcher()
router = Router()
dp.include_router(router)
# Инициализация FastAPI
app = FastAPI()

class FormEmail(StatesGroup):
    email = State()

# Команда /start
@router.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        f'<a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a><a>, Вас приветствует бот для покупки курсов!</a>',
        reply_markup=kb.main)


@router.callback_query(F.data == 'list_courses')
async def send_courses(callback: CallbackQuery):
    await callback.answer('', show_alert=False)
    await callback.message.answer('<i>Вот список доступных курсов!</i>', reply_markup=kb.courses)


@router.callback_query(F.data == 'python')
async def send_python_info(callback: CallbackQuery):
    await callback.message.answer_photo(photo=FSInputFile('python_courses.jpg', filename='pyt'))
    await callback.answer('', show_alert=False)
    await callback.message.answer('<b>Самый лучший курс по программированию на pytnon версии 3.x!!!</b>', reply_markup=kb.buy_or_not)


@router.callback_query(F.data == 'buy')
async def buy_product(callback: CallbackQuery, state: FSMContext):
    await callback.answer('', show_alert=False)
    await state.set_state(FormEmail.email)
    await callback.message.answer("Введите e-mail")


@router.message(FormEmail.email)
async def process_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    email_user = await state.get_data()

    payload = {
        "email": email_user["email"],
        "offerId": "91d59426-775e-41ad-b42b-fef0a5ba54b1",  # ID оффера товара
        "currency": "RUB",
    }
    headers = {
        "accept": "application/json",
        "X-Api-Key": LAVA_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(f"{LAVA_API_URL}/invoice", json=payload, headers=headers, verify=False)
        response.raise_for_status()

        if response.status_code == 201:
            data = response.json()
            payment_url = data.get("paymentUrl")
            await message.reply(f"Оплатите товар по ссылке: {payment_url}")
        else:
            await message.reply("Произошла ошибка при создании платежа.")
    except requests.exceptions.RequestException as e:
        await message.reply(f"Ошибка при запросе к API: {e}")

    await state.clear()


# обработка вебхуков
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    event_type = data.get("eventType")
    contract_id = data.get("contractId")
    buyer_email = data.get("buyer", {}).get("email")
    status = data.get("status")

# уведомление пользователя в доработке, буду делать по факту, тк потестить варианта нет
    if event_type == "payment.success" and status == "completed":
        message = f"Оплата прошла успешно! Контракт: {contract_id}, Email: {buyer_email}"

    return {"status": "ok"}

# Запуск бота
async def start_bot():
    await dp.start_polling(bot)

# Запуск FastAPI
async def start_fastapi():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()

# Основная функция для запуска обоих приложений
async def main():
    await asyncio.gather(
        start_bot(),
        start_fastapi()
    )

if __name__ == '__main__':
    asyncio.run(main())