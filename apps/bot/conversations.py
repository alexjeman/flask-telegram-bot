from apps.bot.api_requests import API, APINew
from apps.bot.models import BotLink, db


def conversation_handler(bot, chat_id, update):
    text = str()
    if update.message.text:
        text = update.message.text.encode('utf-8').decode()

    if "/start " in text:
        bot.send_chat_action(chat_id=chat_id, action="typing")
        parsed_key = text[text.index(" "):].strip()
        check_exists_apikey = bool(BotLink.query.filter_by(key=parsed_key).first())
        check_exists_chat_id = bool(BotLink.query.filter_by(chat_id=chat_id).first())
        if check_exists_apikey:
            bot.sendMessage(chat_id=chat_id, text="Someone already used this key! 👾 \n")

        elif check_exists_chat_id:
            existing_key = BotLink.query.filter_by(chat_id=chat_id).first()
            bot.sendMessage(chat_id=chat_id,
                            text=f"You already have a key registered! ⤵ \n 💃 {existing_key.key} 💃 \n")
        else:
            link_existing = BotLink(
                key=parsed_key,
                chat_id=chat_id
            )
            db.session.add(link_existing)
            db.session.commit()
            bot_message = f"API key {parsed_key}\n"
            bot.sendMessage(chat_id=chat_id, text=bot_message)

    elif text == "/start":
        bot.send_chat_action(chat_id=chat_id, action="typing")
        bot_message = f"Welcome to HostMonitor,\n" \
                      f"I'm HostHunter_bot, and will interface you with our API! 🔥 🤘 \n" \
                      f"/start - Channel intro.\n" \
                      f"/register - Register with HostMonitor and receive a new API key.\n" \
                      f"/myapikey - Get info about my apikey\n"
        return bot_message

    elif text == "/register":
        bot.send_chat_action(chat_id=chat_id, action="typing")
        new_api = APINew(chat_id=chat_id)
        bot_message_pre = f"Requesting new API ✈ ⏰...\n"
        bot.sendMessage(chat_id=chat_id, text=bot_message_pre)

        new_api_request = new_api.get_newkey()
        if f"{new_api_request.status_code}" == "200":
            bot_message_success = f"Your new personal API key is : {new_api_request.json()['apikey']}\n"
            bot.sendMessage(chat_id=chat_id, text=bot_message_success)
            new_botlink = BotLink(
                key=new_api_request.json()['apikey'],
                chat_id=chat_id
            )
            db.session.add(new_botlink)
            db.session.commit()
            print("linked", chat_id, new_api_request.json()['apikey'])

        elif f"{new_api_request.status_code}" == "409":
            bot.sendMessage(chat_id=chat_id, text=f"You are already registered, try some get requests! 🔔\n")

    elif text == "/myapikey":
        bot.send_chat_action(chat_id=chat_id, action="typing")
        new_api_request = API(obj=BotLink, chat_id=chat_id)
        api_request = new_api_request.get_apikey_info()
        host_list = api_request.json()['hosts']
        bot_message = f"Email: {api_request.json()['email'] if api_request.json()['email'] is not None else 'not linked'}\n" \
                      f"Total hosts added: {len(host_list)}\n" \
                      f"{[['Host id: ' + str(hos['id']) + chr(10) + str('Name: ') + str(hos['name'] + chr(10) + str('URL: ') + str(hos['url']) + chr(10))][0] for hos in host_list][0]}" \
            if len(host_list) > 0 \
            else f"Add some hosts to watch! 👽\n"
        bot.sendMessage(chat_id=chat_id, text=bot_message)