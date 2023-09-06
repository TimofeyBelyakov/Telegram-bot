import requests
from envparse import Env


# По сути класс нужен лишь для того, чтобы отправлять запросы боту.
class TelegramClient:
    def __init__(self, token: str, base_url: str):
        self.token = token
        self.base_url = base_url

    def prepare_url(self, method: str) -> str:
        result_url = f"{self.base_url}/bot{self.token}/"
        if method is not None:
            result_url += method
        return result_url

    # Выполняет POST-запрос по сформированной url.
    def post(self, method: str, params: dict = None, data: dict = None) -> dict:
        url = self.prepare_url(method)
        response = requests.post(url, params=params, data=data)
        return response.json()


if __name__ == "__main__":
    base_url = "https://api.telegram.org"
    # Создание переменных окружения.
    env = Env()
    token = env.str("token")
    chat_id = env.int("chat_id")

    telegram_client = TelegramClient(token=token, base_url=base_url)
    params = {"chat_id": chat_id, "text": "текст от telegram_client"}
    response = telegram_client.post("sendMessage", params=params)

    print(response)
