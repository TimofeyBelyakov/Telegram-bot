from clients.sqlite_client import SQLiteClient
from tests.test_sqlite_client.conftest import TEST_DB
from tests.test_sqlite_client.conftest import create_user_fixture, get_users_fixture


# В conftest.py прописаны фикстуры, которые неявно будут выполнены в ходе тестирования.
# Перед первым тестом в базе будет создана таблица с пользователями, которая удаляется после выполнения всех тестов.
# Перед каждым тестом таблица с пользователями очищается.
# Также есть две фикстуры create_user_fixture и get_users_fixture, которые явно передаются в качестве аргументов.


def test_write_to_db(get_users_fixture):
    """Тестирование записи пользователя в базу."""
    insert_user = """INSERT INTO users (user_id, username, chat_id) VALUES (?, ?, ?);"""

    user_id = 12345
    username = "timofey"
    chat_id = 12345

    # Поскольку в этом модуле тестируется запись в базу, то добавление пользователя происходит, очевидно, с помощью
    # SQLiteClient.
    sqlite_client = SQLiteClient(TEST_DB)
    sqlite_client.create_connection()
    sqlite_client.execute_query(query=insert_user, params=(user_id, username, chat_id))

    # А вот извлечение пользователей с помощью sqlite3. Тут представлена фикстура.
    users = get_users_fixture()

    assert len(users) == 1
    assert users[0][0] == user_id
    assert users[0][1] == username
    assert users[0][2] == chat_id


def test_read_from_db(create_user_fixture):
    """Тестирование чтения из базы."""
    user_id = 12345
    username = "timofey"
    chat_id = 12345

    # Поскольку в этом модуле тестируется чтение из базы, то добавление пользователя происходит, наоборот, с помощью
    # sqlite3. Тут представлена фикстура.
    create_user_fixture(user_id=user_id, username=username, chat_id=chat_id)

    select_users = """SELECT * FROM users;"""

    # А вот извлечение пользователей с помощью SQLiteClient.
    sqlite_client = SQLiteClient(TEST_DB)
    sqlite_client.create_connection()
    users = sqlite_client.execute_select_query(query=select_users)

    assert len(users) == 1
    assert users[0][0] == user_id
    assert users[0][1] == username
    assert users[0][2] == chat_id
