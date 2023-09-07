import sqlite3


# Простой sqlite клиент.
class SQLiteClient:
    def __init__(self, path: str):
        self.path = path
        self.conn = None

    # Подключение к базе данных.
    def create_conn(self):
        self.conn = sqlite3.connect(self.path, check_same_thread=False)

    # Выполнение команд по внесению изменений в базу данных.
    def execute_query(self, query: str, params: tuple):
        if self.conn is not None:
            self.conn.execute(query, params)
            self.conn.commit()
        else:
            raise ConnectionError("You need to create connection to database!")

    # Выполнение select запросов к базе данных.
    def execute_select_query(self, query: str):
        if self.conn is not None:
            cur = self.conn.cursor()
            cur.execute(query)
            return cur.fetchall()
        else:
            raise ConnectionError("You need to create connection to database!")


if __name__ == "__main__":
    # Создание базы данных.
    CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS users (
            user_id int PRIMARY KEY,
            username text,
            chat_id int
        )
    """

    sqlite_client = SQLiteClient("users.db")
    sqlite_client.create_conn()
    sqlite_client.execute_query(CREATE_TABLE, ())
