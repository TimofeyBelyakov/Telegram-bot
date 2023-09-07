from clients.sqlite_client import SQLiteClient
from datetime import date


# Класс для работы с пользователем в базе данных.
class UserActioner:
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

    # Подключение к базе данных.
    def setup(self):
        self.sqlite_client.create_conn()

    # Закрытие соединения.
    def shutdown(self):
        self.sqlite_client.close_conn()

    # Добавление пользователя в базу данных.
    def create_user(self, user_id: int, username: str, chat_id: int):
        self.sqlite_client.execute_query(self.__CREATE_USER, (user_id, username, chat_id))

    # Получение пользователя из базы данных.
    def get_user(self, user_id: int):
        user = self.sqlite_client.execute_select_query(self.__GET_USER % user_id)
        return user[0] if user else None  # Предполагается, что пользователь с таким user_id один.

    def update_date(self, user_id: int, updated_date: date):
        self.sqlite_client.execute_query(self.__UPDATE_LAST_DATE, (updated_date, user_id))


if __name__ == "__main__":
    user_actioner = UserActioner(SQLiteClient("users.db"))
    user_actioner.setup()
    user_actioner.create_user(12345, "tim", 12345)
    print(user_actioner.get_user(12345))
