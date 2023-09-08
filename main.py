import telebot
from telebot.types import Message
import json
from datetime import datetime
from envparse import Env
from clients.telegram_client import TelegramClient
from clients.sqlite_client import SQLiteClient
from user_actioner import UserActioner
from logging import getLogger, StreamHandler
from datetime import date


# Логирование.
logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("INFO")

# Создание переменных окружения.
env = Env()
TOKEN = env.str("TOKEN")
ADMIN_CHAT_ID = env.int("ADMIN_CHAT_ID")

base_url = "https://api.telegram.org"
db = "users.db"


class MyBot(telebot.TeleBot):
    """Расширение базового класса telebot.TeleBot."""
    def __init__(self, telegram_client: TelegramClient, user_actioner: UserActioner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавление новых полей.
        self.telegram_client = telegram_client
        self.user_actioner = user_actioner

    def setup_resources(self):
        """Метод для подключения к базе данных."""
        self.user_actioner.setup()

    def shutdown_resources(self):
        """Метод для закрытия соединения с базой данных."""
        self.user_actioner.shutdown()


# Бот.
bot = MyBot(
    token=TOKEN,
    telegram_client=TelegramClient(token=TOKEN, base_url=base_url),
    user_actioner=UserActioner(SQLiteClient(db))
)


@bot.message_handler(commands=["start"])
def start(message: Message):
    """Обработка команды /start. Регистрация пользователя."""
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
        data_from_json[str(user_id)] = {"username": username, "chat_id": chat_id, "last_updated_date": None}

    # Записываем пользователей в json файл.
    with open("users.json", "w") as file:
        json.dump(data_from_json, file, indent=4, ensure_ascii=False)

    # Отвечаем пользователю.
    bot.reply_to(message=message, text=f"ты {'уже' if not create_new_user else ''} зарегистрирован: {username}, "
                                       f"твой user_id: {user_id}")


def handle_speech(message: Message):
    """Генерирует ответ на сообщение от пользователя."""
    with open("users.json", "r") as file:
        data_from_json = json.load(file)

    # Изменение даты ответа пользователя.
    user_id = message.from_user.id
    date_now = date.today()
    data_from_json[str(user_id)]["last_updated_date"] = str(date_now)
    bot.user_actioner.update_date(user_id=message.from_user.id, updated_date=date_now)

    with open("users.json", "w") as file:
        json.dump(data_from_json, file, indent=4, ensure_ascii=False)

    bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"чмоня {message.from_user.username} говорит: {message.text}")
    bot.reply_to(message=message, text="мне не интересно")


@bot.message_handler(commands=["say_speech"])
def say_speech(message: Message):
    """Обработка команды /say_speech."""
    bot.reply_to(message=message, text="чем занят лох?")
    # Если пользователь ответил боту, то вызывается handle_speech().
    bot.register_next_step_handler(message, callback=handle_speech)


def create_err_message(err: Exception) -> str:
    """Генерирует сообщение об ошибке."""
    return f"{datetime.now()}\n{err.__class__} :: {err}"


# Если произойдёт ошибка, то отправится соответствующее сообщение и бот перезапустится.
while True:
    try:
        # Подключение к базе данных.
        bot.setup_resources()
        bot.polling()
    except Exception as err:
        err_message = create_err_message(err)
        # Отправляем сообщение об ошибке в чат.
        bot.telegram_client.post(method="sendMessage", params={"chat_id": ADMIN_CHAT_ID, "text": err_message})
        # Логирование ошибки.
        logger.error(err_message)
        # Закрытие соединения.
        bot.shutdown_resources()
