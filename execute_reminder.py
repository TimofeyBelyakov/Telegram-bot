from clients.sqlite_client import SQLiteClient
from clients.telegram_client import TelegramClient
from workers.reminder import Reminder
from logging import getLogger, StreamHandler
from envparse import Env
from datetime import datetime
import time


# Логирование.
logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("INFO")

# Создание переменных окружения.
env = Env()
TOKEN = env.str("TOKEN")
FROM_TIME = env.str("FROM_TIME")
TO_TIME = env.str("TO_TIME")

base_url = "https://api.telegram.org"
db = "users.db"

# Объект напоминалки.
reminder = Reminder(
    telegram_client=TelegramClient(token=TOKEN, base_url=base_url),
    sqlite_client=SQLiteClient(db)
)
reminder.setup()

start_time = datetime.strptime(FROM_TIME, "%H:%M:%S").time()  # время, с которого начинается рассылка напоминаний
end_time = datetime.strptime(TO_TIME, "%H:%M:%S").time()  # время, до которого идёт рассылка напоминаний

while True:
    now_time = datetime.now().time()  # текущее время
    # Если текущее время попадает в диапазон, то напоминаем каждые 15 секунд.
    if start_time <= now_time <= end_time:
        reminder()
        time.sleep(15)
    # Если за пределами диапазона, то спим 1 час.
    else:
        time.sleep(3600)
