from apps.bot.api_requests import APIHost
import json


def callback_handler(bot, chat_id, query):
    callback_json = json.loads(query.data)

    if "mute" in callback_json["action"]:
        bot.send_chat_action(chat_id=chat_id, action="typing")
        api_host = APIHost(chat_id=chat_id, callback_json=callback_json)
        request_callback = api_host.mute_host()
        response = request_callback.json()
        return "Host was muted." if response["muted"] else "Host is active."

    elif "delete" in callback_json["action"]:
        bot.send_chat_action(chat_id=chat_id, action="typing")
        api_host = APIHost(chat_id=chat_id, callback_json=callback_json)
        request_callback = api_host.delete()
        response = request_callback.json()
        try:
            deleted = response["url"]
            return "Host was deleted."
        except:
            return "Host could not be found."

    elif "get_host" in callback_json["action"]:
        bot.send_chat_action(chat_id=chat_id, action="typing")
        api_host = APIHost(chat_id=chat_id, callback_json=callback_json)
        request_callback = api_host.get_one()
        hosts = request_callback.json()
        message = str()
        for item in hosts:
            message += f"{item['time']} | http {item['code']} | {item['response_time']} ms \n"
        return message
