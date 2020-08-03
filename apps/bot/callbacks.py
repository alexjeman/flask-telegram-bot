from apps.bot.api_requests import API, APINew, APILink, APIHost
import sys
from apps.bot.models import BotLink, db
import json


def callback_handler(bot, chat_id, query):
    callback_json = json.loads(query.data)

    if "mute" in callback_json["action"]:
        print("Callback action:", callback_json["muted"], file=sys.stderr)
        api_host = APIHost(chat_id=chat_id, callback_json=callback_json)
        request_callback = api_host.mute_host()
        return "Host was muted." if request_callback.json()["muted"] else "Host is active."

    elif "get_host" in callback_json["action"]:
        print("Callback action get:", callback_json["hostid"], file=sys.stderr)
        api_host = APIHost(chat_id=chat_id, callback_json=callback_json)
        request_callback = api_host.get_one()
        hosts = request_callback.json()
        message = str()
        for item in hosts:
            message += item['time'] + ' | http ' + item['code'] + ' | ' + item['response_time'] + ' ms' + chr(10)
        return message
