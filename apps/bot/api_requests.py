import requests
from config import Settings
settings = Settings()


class API:
    def __init__(self, obj, chat_id, api_url=settings.API_URL):
        self.chat_id = chat_id
        self.api_url = api_url
        self.obj = obj

    def get_apikey_info(self):
        my_key = self.obj.query.filter_by(chat_id=self.chat_id).first()
        response = requests.get(f"{self.api_url}apikey/{my_key.key}")
        return response


class APINew:
    def __init__(self, chat_id, api_url=settings.API_URL):
        self.chat_id = chat_id
        self.api_url = api_url

    def get_newkey(self):
        body = {"chat_id": f"{self.chat_id}"}
        response = requests.post(self.api_url + "apikey/", json=body)
        return response
