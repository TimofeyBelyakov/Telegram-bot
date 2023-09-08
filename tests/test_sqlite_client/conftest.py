import pytest
import sqlite3


TEST_DB = "tests/test_sqlite_client/test_users.db"


@pytest.fixture(scope="session")
def db_connection():
    """Фикстура для подключения к базе данных."""
    return sqlite3.connect(TEST_DB)


# scope="session" говорит о том, что фикстура будет выполнена до и после выполнения всех тестов из директории
# tests.test_sqlite_client.
# autouse=True говорит о том, что фикстуру необходимо автоматически выполнять для каждой тестовой функции. Поскольку
# значение scope - "session", то фикстура будет выполнена до выполнения первого модуля и после последнего.
# Фикстура, как и тестовая функция, может принимать фикстуру в качестве аргумента.
@pytest.fixture(scope="session", autouse=True)
def create_and_drop_test_table(db_connection):
    """Фикстура для создания тестовой таблицы с пользователями."""
    create_table_users = """
                CREATE TABLE IF NOT EXISTS users (
                    user_id int PRIMARY KEY,
                    username text,
                    chat_id int,
                    last_updated_date date
                )
            """

    # База данных создаётся и удаляется не с помощью SQLiteClient, а с помощью модуля sqlite3. Это связано с тем, что в
    # каждом тесте с помощью SQLiteClient тестируется лишь определённый метод.
    db_connection.execute(create_table_users)
    db_connection.commit()

    # Код после yield запустится уже после выполнения всех тестов.
    yield None

    # Удаление таблицы с пользователями.
    db_connection.execute("""DROP TABLE users;""")
    db_connection.commit()


# scope="function" говорит о том, что фикстура будет запущена до выполнения тестовой функции.
# autouse=True говорит о том, что фикстуру необходимо автоматически запускать для каждой тестовой функции.
@pytest.fixture(scope="function", autouse=True)
def clean_table(db_connection):
    """Фикстура для очищения тестовой таблицы с пользователями."""
    db_connection.execute("""DELETE FROM users;""")
    db_connection.commit()


@pytest.fixture(scope="session")
def create_user_fixture(db_connection):
    """Фикстура, возвращающая функцию добавления пользователя в базу."""
    def create_user(user_id: int, username: str, chat_id: int):
        """Функция добавления пользователя в базу."""
        db_connection.execute(
            """INSERT INTO users (user_id, username, chat_id) VALUES (?, ?, ?);""",
            (user_id, username, chat_id)
        )
        db_connection.commit()
    return create_user


@pytest.fixture(scope="session")
def get_users_fixture(db_connection):
    """Фикстура, возвращающая функцию получения всех пользователей из базы."""
    def get_users():
        """Функция получения всех пользователей из базы."""
        cursor = db_connection.cursor()
        cursor.execute("""SELECT * FROM users;""")
        return cursor.fetchall()
    return get_users
