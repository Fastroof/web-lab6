from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

location = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Надати геодані", request_location=True)]],
                               resize_keyboard=True)
menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Дізнатися погоду ☁")],
                                     [KeyboardButton(text="Дізнатися курс валют $€")]],
                               resize_keyboard=True)
weather = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Дізнатися погоду зараз")],
                                     [KeyboardButton(text="Дізнатися погоду на завтра")],
                                     [KeyboardButton(text="Дізнатися погоду на 5 днів")],
                                     [KeyboardButton(text="Змінити локацію")],
                                     [KeyboardButton(text="До меню")]],
                               resize_keyboard=True)
curr = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Дізнатися курс долара")],
                                     [KeyboardButton(text="Дізнатися курс євро")],
                                     [KeyboardButton(text="До меню")]],
                               resize_keyboard=True)