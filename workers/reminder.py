from clients.sqlite_client import SQLiteClient
from clients.telegram_client import TelegramClient
from logging import getLogger, StreamHandler
from envparse import Env


# Логирование.
logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("INFO")

# Создание переменных окружения.
env = Env()
TOKEN = env.str("TOKEN")


class Reminder:
    """Класс напоминалки."""
    __GET_TASKS = """
        SELECT chat_id from users WHERE last_updated_date IS NULL OR last_updated_date < date('now');
    """

    def __init__(self, telegram_client: TelegramClient, sqlite_client: SQLiteClient):
        self.telegram_client = telegram_client
        self.sqlite_client = sqlite_client
        self.set_up = False

    def setup(self):
        """Подключение к базе данных."""
        self.sqlite_client.create_connection()
        self.set_up = True

    def shutdown(self):
        """Закрытие соединения."""
        self.sqlite_client.close_connection()

    def notify(self, chat_ids: list):
        """Рассылка напоминаний пользователям."""
        for chat_id in chat_ids:
            response = self.telegram_client.post(method="sendMessage", params={
                "text": "*пинок под зад*",
                "chat_id": chat_id
            })
            logger.info(response)

    def execute(self):
        """Поиск пользователей, не отправивших сегодня сообщение, и вызов напоминалки."""
        # Извлечение пользователей, не отправивших сегодня сообщение.
        chat_ids = self.sqlite_client.execute_select_query(query=self.__GET_TASKS)
        if chat_ids:
            # Вызов напоминалки
            self.notify(chat_ids=[tuple_chat_id[0] for tuple_chat_id in chat_ids])

    # Магический метод делает экземпляр вызываемым.
    def __call__(self, *args, **kwargs):
        # Если worker не был подключён к базе, то возвращается None с логом об ошибке.
        if not self.set_up:
            logger.error("Resources in worker haven't been set up!")
            return None
        # Иначе запускается напоминалка.
        self.execute()


if __name__ == "__main__":
    base_url = "https://api.telegram.org"
    db = "../users.db"

    reminder = Reminder(
        telegram_client=TelegramClient(token=TOKEN, base_url=base_url),
        sqlite_client=SQLiteClient(db)
    )
    reminder.setup()
    # Запуск напоминалки.
    reminder()
