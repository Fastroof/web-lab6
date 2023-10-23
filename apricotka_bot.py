import logging
import sys
from os import getenv

import requests
from aiogram import F, Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

import keyboard

TOKEN = getenv("BOT_TOKEN")
WEB_SERVER_HOST = "::"
WEB_SERVER_PORT = 8350
WEBHOOK_PATH = "/bot/"
BASE_WEBHOOK_URL = "https://fastroof.alwaysdata.net/"
WEBHOOK_SECRET = "my-secret"  # (optional)
WEATHER_API_KEY = getenv("WEATHER_API_KEY")
CURRENT_WEATHER_API_CALL = 'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid='
FORECAST_WEATHER_API_CALL = 'https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid='
CURRENCY_API_CALL = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'

router = Router()
user_data = {}


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    user_data[message.from_user.id] = {}
    full_name = message.from_user.full_name
    user_data[message.from_user.id]['full_name'] = full_name
    await message.answer(
        f"Вітаю, {hbold(full_name)}.\nЦей бот допоможе вам дізнатися погоду та курс валют\n",
        reply_markup=keyboard.menu)


@router.message(F.text == 'Дізнатися погоду ☁')
async def weather_handler(message: Message) -> None:
    user_id = message.from_user.id
    if user_id in user_data:
        user_info = user_data[user_id]
        if 'lat' in user_info and 'lon' in user_info:
            await message.answer('🕹 Оберіть активність', reply_markup=keyboard.weather)
        else:
            await message.answer(
                "Будь ласка, надайте локацію з якою будемо працювати.\n"
                f"Це можна зробити натиснувши на {hbold('Надати геодані')}, "
                f"або написавши напряму, наприклад: {hbold('40.193889 33.774722')}",
                reply_markup=keyboard.location)


@router.message(F.text == 'Змінити локацію')
async def change_geo_handler(message: Message) -> None:
    user_id = message.from_user.id
    if user_id in user_data:
        user_data[user_id] = {}
        await message.answer(
            "Будь ласка, надайте нову локацію з якою будемо працювати.\n"
            f"Це можна зробити натиснувши на {hbold('Надати геодані')}, "
            f"або написавши напряму, наприклад: {hbold('40.193889 33.774722')}",
            reply_markup=keyboard.location)


@router.message(F.text == 'До меню')
async def to_menu_handler(message: Message) -> None:
    await message.answer('🕹 Оберіть активність', reply_markup=keyboard.menu)


@router.message(F.text == 'Дізнатися курс валют $€')
async def curr_handler(message: Message) -> None:
    await message.answer('🕹 Оберіть активність', reply_markup=keyboard.curr)


@router.message(F.text == 'Надати геодані')
async def geo_handler(message: Message) -> None:
    user_id = message.from_user.id
    if user_id in user_data:
        user_info = user_data[user_id]
        lat = message.location.latitude
        lon = message.location.longitude
        user_info['lat'] = lat
        user_info['lon'] = lon
        await message.answer(f"Latitude: {lat}\nLongitude: {lon}", reply_markup=keyboard.weather)
    else:
        await message.answer(f"Для початку напишіть {hbold('/start')}", reply_markup=types.ReplyKeyboardRemove())


@router.message(F.text.regexp(r'^-?[0-9]{1,2}\.[0-9]{6} -?[0-9]{1,3}\.[0-9]{6}$'))
async def manual_geo_handler(message: Message) -> None:
    user_id = message.from_user.id
    if user_id in user_data:
        user_info = user_data[user_id]
        location = message.text.split()
        lat = location[0]
        lon = location[1]
        user_info['lat'] = lat
        user_info['lon'] = lon
        await message.answer(f"Latitude: {lat}\nLongitude: {lon}", reply_markup=keyboard.weather)
    else:
        await message.answer(f"Для початку напишіть {hbold('/start')}", reply_markup=types.ReplyKeyboardRemove())


@router.message(F.text == 'Дізнатися погоду зараз')
async def current_weather_handler(message: Message) -> None:
    user_id = message.from_user.id
    if user_id in user_data:
        user_info = user_data[user_id]
        lat = user_info["lat"]
        lon = user_info["lon"]
        r = requests.get(
            CURRENT_WEATHER_API_CALL.format(latitude=lat, longitude=lon) + WEATHER_API_KEY + '&units=metric')
        response = r.json()
        temp = response["main"]["temp"]
        pressure = response["main"]["pressure"]
        humidity = response["main"]["humidity"]
        wind_speed = response["wind"]["speed"]
        weather_description = response["weather"][0]["description"]
        await message.answer(f"Температура: {temp}℃\nТиск: {pressure}Па\nВологість: {humidity}%\n"
                             f"Вітер : {wind_speed}м/с\nПогода: {weather_description}",
                             reply_markup=keyboard.weather)


@router.message(F.text == 'Дізнатися погоду на завтра')
async def tomorrow_weather_handler(message: Message) -> None:
    user_id = message.from_user.id
    if user_id in user_data:
        user_info = user_data[user_id]
        lat = user_info["lat"]
        lon = user_info["lon"]
        r = requests.get(
            FORECAST_WEATHER_API_CALL.format(latitude=lat, longitude=lon) + WEATHER_API_KEY + '&units=metric&cnt=8')
        response = r.json()
        elem_list = response["list"]
        for i in [1, 3, 5, 7]:
            elem = elem_list[i]
            date = elem["dt_txt"]
            temp = elem["main"]["temp"]
            pressure = elem["main"]["pressure"]
            humidity = elem["main"]["humidity"]
            wind_speed = elem["wind"]["speed"]
            weather_description = elem["weather"][0]["description"]
            await message.answer(f"Час: {date}\nТемпература: {temp}℃\n"
                                 f"Тиск: {pressure}Па\nВологість: {humidity}%\nШвидкість вітру : {wind_speed}м/с\n"
                                 f"Погода: {weather_description}",
                                 reply_markup=keyboard.weather)


@router.message(F.text == 'Дізнатися погоду на 5 днів')
async def forecast_weather_handler(message: Message) -> None:
    user_id = message.from_user.id
    if user_id in user_data:
        user_info = user_data[user_id]
        lat = user_info["lat"]
        lon = user_info["lon"]
        r = requests.get(
            FORECAST_WEATHER_API_CALL.format(latitude=lat, longitude=lon) + WEATHER_API_KEY + '&units=metric')
        response = r.json()
        day_list = response["list"]
        for i in [4, 12, 20, 28, 36]:
            day = day_list[i]
            date = day["dt_txt"]
            temp = day["main"]["temp"]
            pressure = day["main"]["pressure"]
            humidity = day["main"]["humidity"]
            wind_speed = day["wind"]["speed"]
            weather_description = day["weather"][0]["description"]
            await message.answer(f"Дата: {date}\nТемпература: {temp}℃\n"
                                 f"Тиск: {pressure}Па\nВологість: {humidity}%\nШвидкість вітру : {wind_speed}м/с\n"
                                 f"Погода: {weather_description}",
                                 reply_markup=keyboard.weather)


@router.message(F.text == 'Дізнатися курс долара')
async def usd_handler(message: Message) -> None:
    r = requests.get(CURRENCY_API_CALL)
    response = r.json()
    curr = response[1]
    buy = curr["buy"][:5]
    sale = curr["sale"][:5]
    await message.answer(f"Купівля: {buy}грн\nПродаж: {sale}грн\n",
                         reply_markup=keyboard.curr)


@router.message(F.text == 'Дізнатися курс євро')
async def eur_handler(message: Message) -> None:
    r = requests.get(CURRENCY_API_CALL)
    response = r.json()
    curr = response[0]
    buy = curr["buy"][:5]
    sale = curr["sale"][:5]
    await message.answer(f"Купівля: {buy}грн\nПродаж: {sale}грн\n",
                         reply_markup=keyboard.curr)


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(on_startup)

    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
