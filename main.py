import telebot
from telebot.types import Message
import json
from datetime import datetime
from envparse import Env
from telegram_client import TelegramClient
from sqlite_client import SQLiteClient
from user_actioner import UserActioner


# Создание переменных окружения.
env = Env()
TOKEN = env.str("TOKEN")
ADMIN_CHAT_ID = env.int("ADMIN_CHAT_ID")

base_url = "https://api.telegram.org"
db = "users.db"


# Расширение базового класса.
class MyBot(telebot.TeleBot):
    def __init__(self, telegram_client: TelegramClient, user_actioner: UserActioner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавление новых полей.
        self.telegram_client = telegram_client
        self.user_actioner = user_actioner

    # Метод для подключения к базе данных.
    def setup_resources(self):
        self.user_actioner.setup()


# Бот.
bot = MyBot(
    token=TOKEN,
    telegram_client=TelegramClient(token=TOKEN, base_url=base_url),
    user_actioner=UserActioner(SQLiteClient(db))
)
bot.setup_resources()


# Обработка команды /start. Регистрация пользователя.
@bot.message_handler(commands=["start"])
def start(message: Message):
    # В users.json хранятся зарегистрированные пользователи.
    with open("users.json", "r") as file:
        # Считываем зарегистрированных пользователей.
        data_from_json = json.load(file)

    # Данные от пользователя.
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id

    # Если пользователя нет, то добавляем его в базу sqlite.
    create_new_user = False
    user = bot.user_actioner.get_user(user_id=user_id)
    if user is None:
        bot.user_actioner.create_user(user_id=user_id, username=username, chat_id=chat_id)
        create_new_user = True

    # Если пользователя нет, то добавляем его в json объект.
    if str(user_id) not in data_from_json:
        data_from_json[user_id] = {"username": username, "chat_id": chat_id}

    # Записываем пользователей в json файл.
    with open("users.json", "w") as file:
        json.dump(data_from_json, file, indent=4, ensure_ascii=False)

    # Отвечаем пользователю.
    bot.reply_to(message=message, text=f"ты {'уже' if not create_new_user else ''} зарегистрирован: {username}, "
                                       f"твой user_id: {user_id}")


# Генерирует ответ на сообщение от пользователя.
def handle_speech(message: Message):
    bot.reply_to(message=message, text="мне не интересно")


# Обработка команды /say_speech.
@bot.message_handler(commands=["say_speech"])
def say_speech(message: Message):
    bot.reply_to(message=message, text="чем занят лох?")
    # Если пользователь ответил боту, то вызывается handle_speech().
    bot.register_next_step_handler(message, callback=handle_speech)


# Если произойдёт ошибка, то отправится соответствующее сообщение и бот перезапустится.
while True:
    try:
        bot.polling()
    except Exception as err:
        params = {
            "chat_id": ADMIN_CHAT_ID,
            "text": f"{datetime.now()}\n{err.__class__} :: {err}"
        }
        # Отправляем сообщение об ошибке в чат.
        bot.telegram_client.post(method="sendMessage", params=params)
