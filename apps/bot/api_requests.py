import requests
from apps.bot.models import BotLink
from config import Settings

settings = Settings()


class API:
    def __init__(self, chat_id, api_url=settings.API_URL):
        self.chat_id = chat_id
        self.api_url = api_url

    def get_apikey_info(self):
        my_key = BotLink.query.filter_by(chat_id=self.chat_id).first()
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


class APILink:
    def __init__(self, chat_id, apikey, api_url=settings.API_URL):
        self.chat_id = chat_id
        self.apikey = apikey
        self.api_url = api_url

    def link_existing(self):
        body = {"chat_id": f"{self.chat_id}"}
        response = requests.post(self.api_url + f"apikey/{self.apikey}/", json=body)
        return response


class APIHost:
    def __init__(self,  chat_id, callback_json=None, api_url=settings.API_URL):
        self.chat_id = chat_id
        self.callback_json = callback_json
        self.api_url = api_url

    def mute_host(self):
        my_key = BotLink.query.filter_by(chat_id=self.chat_id).first()
        body = {"muted": self.callback_json["muted"]}
        response = requests.put(self.api_url + f"hosts/{self.callback_json['hostid']}/{my_key.key}/", json=body)
        return response

    def get_all(self):
        my_key = BotLink.query.filter_by(chat_id=self.chat_id).first()
        response = requests.get(self.api_url + f"hosts/{my_key.key}/")
        return response

    def get_one(self):
        my_key = BotLink.query.filter_by(chat_id=self.chat_id).first()
        response = requests.get(self.api_url + f"hosts/{self.callback_json['hostid']}/{my_key.key}/")
        return response
