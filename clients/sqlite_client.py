import sqlite3


class SQLiteClient:
    """Простой sqlite клиент."""
    def __init__(self, path: str):
        self.path = path
        self.connection = None

    def create_connection(self):
        """Подключение к базе данных."""
        self.connection = sqlite3.connect(database=self.path, check_same_thread=False)

    def close_connection(self):
        """Закрытие соединения."""
        self.connection.close()

    def execute_query(self, query: str, params: tuple):
        """Выполнение команд по внесению изменений в базу данных."""
        if self.connection is not None:
            self.connection.execute(query, params)
            self.connection.commit()
        else:
            raise ConnectionError("You need to create connection to database!")

    def execute_select_query(self, query: str):
        """Выполнение select запросов к базе данных."""
        if self.connection is not None:
            cursor = self.connection.cursor()
            cursor.execute(query)
            return cursor.fetchall()
        else:
            raise ConnectionError("You need to create connection to database!")


if __name__ == "__main__":
    # Создание базы данных.
    CREATE_TABLE_USERS = """
        CREATE TABLE IF NOT EXISTS users (
            user_id int PRIMARY KEY,
            username text,
            chat_id int,
            last_updated_date date
        )
    """

    sqlite_client = SQLiteClient("users.db")
    sqlite_client.create_connection()
    sqlite_client.execute_query(CREATE_TABLE_USERS, ())
