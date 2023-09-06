import telebot
from telebot.types import Message
import json
from datetime import datetime
from envparse import Env
from telegram_client import TelegramClient


# Создание переменных окружения.
env = Env()
TOKEN = env.str("TOKEN")
ADMIN_CHAT_ID = env.int("ADMIN_CHAT_ID")


# Расширение базового класса.
class MyBot(telebot.TeleBot):
    def __init__(self, telegram_client: TelegramClient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавление нового поля.
        self.telegram_client = telegram_client


base_url = "https://api.telegram.org"
telegram_client = TelegramClient(token=TOKEN, base_url=base_url)
bot = MyBot(token=TOKEN, telegram_client=telegram_client)


# Обработка команды /start.
@bot.message_handler(commands=["start"])
def start(message: Message):
    # В users.json хранятся зарегистрированные пользователи.
    with open("users.json", "r") as file:
        data_from_json = json.load(file)
    user_id = message.from_user.id
    username = message.from_user.username
    if str(user_id) not in data_from_json:
        data_from_json[user_id] = {"username": username}
    with open("users.json", "w") as file:
        json.dump(data_from_json, file, indent=4, ensure_ascii=False)
    bot.reply_to(message=message, text=f"ты зарегистрирован: {username}")


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
        bot.telegram_client.post(method="sendMessage", params=params)
