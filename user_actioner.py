from clients.sqlite_client import SQLiteClient
from datetime import date


class UserActioner:
    """Класс для работы с пользователем в базе данных."""
    __CREATE_USER = """
        INSERT INTO users (user_id, username, chat_id) VALUES (?, ?, ?);
    """
    __GET_USER = """
        SELECT user_id, username, chat_id, last_updated_date FROM users WHERE user_id = %s;
    """
    __UPDATE_LAST_DATE = """
        UPDATE users SET last_updated_date = ? WHERE user_id = ?;
    """

    def __init__(self, sqlite_client: SQLiteClient):
        self.sqlite_client = sqlite_client

    def setup(self):
        """Подключение к базе данных."""
        self.sqlite_client.create_connection()

    def shutdown(self):
        """Закрытие соединения."""
        self.sqlite_client.close_connection()

    def create_user(self, user_id: int, username: str, chat_id: int):
        """Добавление пользователя в базу данных."""
        self.sqlite_client.execute_query(query=self.__CREATE_USER, params=(user_id, username, chat_id))

    def get_user(self, user_id: int):
        """Получение пользователя из базы данных."""
        user = self.sqlite_client.execute_select_query(query=self.__GET_USER % user_id)
        return user[0] if user else None  # Предполагается, что пользователь с таким user_id один.

    def update_date(self, user_id: int, updated_date: date):
        """Обновление даты последнего отправленного пользователем сообщения."""
        self.sqlite_client.execute_query(query=self.__UPDATE_LAST_DATE, params=(updated_date, user_id))


if __name__ == "__main__":
    user_id = 12345
    username = "tim"
    chat_id = 12345

    user_actioner = UserActioner(SQLiteClient("users.db"))
    user_actioner.setup()
    user_actioner.create_user(user_id=user_id, username=username, chat_id=chat_id)
    print(user_actioner.get_user(user_id=user_id))
