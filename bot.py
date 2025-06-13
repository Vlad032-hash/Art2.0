import logging
import os
import requests
from aiogram import Bot, Dispatcher, types, executor
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
SHOP_ID = os.getenv("SHOP_ID")
SECRET_KEY = os.getenv("SECRET_KEY")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

products = {
    "1": {"name": "Тишина", "price": 3000, "url": "https://t.me/Silence_323232"},
    "2": {"name": "Город без времени", "price": 7000, "url": "https://t.me/gorodbezvremeni"},
    "3": {"name": "Цифровая Вселенная", "price": 10000, "url": "https://t.me/Digital_Universe32"},
}

user_orders = {}

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for pid, product in products.items():
        keyboard.add(types.KeyboardButton(f"{product['name']} - {product['price']} ₽"))
    await message.answer("Привет! Выбери арт для покупки:", reply_markup=keyboard)

@dp.message_handler(commands=['check'])
async def check_payment(message: types.Message):
    args = message.text.split()
    if len(args) != 2:
        await message.answer("Отправь команду в формате:\n/check <payment_id>")
        return
    payment_id = args[1]
    result = check_payment_status(payment_id)
    if not result:
        await message.answer("Платеж не найден или не оплачен.")
        return
    user_id = message.from_user.id
    if user_id not in user_orders:
        await message.answer("Не найден заказ. Сначала выбери товар.")
        return
    product_id = user_orders[user_id]
    product = products.get(product_id)
    if not product:
        await message.answer("Ошибка. Свяжись с админом.")
        return
    await message.answer(f"Оплата подтверждена!\nСсылка на арт: {product['url']}")
    del user_orders[user_id]

@dp.message_handler()
async def handle_product_choice(message: types.Message):
    text = message.text
    for pid, product in products.items():
        if product['name'] in text:
            user_orders[message.from_user.id] = pid
            payment_link = create_payment_link(pid, product)
            await message.answer(f"Ссылка для оплаты:\n{payment_link}\n\nПосле оплаты пришли /check <payment_id>")
            return
    await message.answer("Не понял команду. Выбери товар из списка.")

def create_payment_link(product_id, product):
    return (f"https://yookassa.ru/pay?shopId={SHOP_ID}&amount={product['price']}"
            f"&product={product_id}&orderNumber={product_id}")

def check_payment_status(payment_id):
    url = f"https://api.yookassa.ru/v3/payments/{payment_id}"
    try:
        response = requests.get(url, auth=(SHOP_ID, SECRET_KEY))
        if response.status_code == 200:
            data = response.json()
            return data.get("status") == "succeeded"
        return False
    except Exception as e:
        logging.error(f"Ошибка при проверке оплаты: {e}")
        return False

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
