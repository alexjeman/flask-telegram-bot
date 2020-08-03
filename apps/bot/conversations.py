import json

from apps.bot.api_requests import API, APINew, APILink, APIHost
from apps.bot.models import BotLink, db
import telegram


def conversation_handler(bot, chat_id, update):
    text = update.message.text.encode('utf-8').decode()

    main_menu_buttons = [
        [telegram.InlineKeyboardButton(text="/start"),
         telegram.InlineKeyboardButton(text="/register")],
        [telegram.InlineKeyboardButton(text="/info"),
         telegram.InlineKeyboardButton(text="/hosts")]
    ]
    main_keyboard = telegram.ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True)

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
            api_request = APILink(chat_id=chat_id, apikey=parsed_key)
            new_api_request = api_request.link_existing()
            if f"{new_api_request.status_code}" == "200":
                link_existing = BotLink(
                    key=parsed_key,
                    chat_id=chat_id
                )
                db.session.add(link_existing)
                db.session.commit()
                bot_message = f"API key {parsed_key} successfully linked! \nTry /add <url> to start monitoring a host.\n"
                bot.sendMessage(chat_id=chat_id, text=bot_message)

    elif "/add " in text:
        bot.send_chat_action(chat_id=chat_id, action="typing")
        parsed_host = text[text.index(" "):].strip()
        new_host = APIHost(chat_id=chat_id, callback_json=parsed_host)
        qpi_response = new_host.add_host()
        if f"{qpi_response.status_code}" == "201":
            api_response_format = str()
            api_response_format += 'Host id: ' + str(qpi_response.json()['id']) + chr(10) + 'Muted: ' + \
                                   str(qpi_response.json()['muted']) + chr(10) + 'URL: ' + qpi_response.json()[
                                       'url'] + chr(10)
            bot.sendMessage(chat_id=chat_id, text=api_response_format, disable_web_page_preview=True)
        elif f"{qpi_response.status_code}" == "400":
            bot.sendMessage(chat_id=chat_id, text=qpi_response.json()['message'])

    elif text == "/add":
        bot.send_chat_action(chat_id=chat_id, action="typing")
        bot.sendMessage(chat_id=chat_id, text="Usage example, type in chat: /add https://www.google.com/")

    elif text == "/menu":
        bot.sendMessage(chat_id=chat_id, text="Select from the menu.", reply_markup=main_keyboard)

    elif text == "/start":
        bot.send_chat_action(chat_id=chat_id, action="typing")
        bot_message = f"Welcome to HostMonitor,\n" \
                      f"I'm HostHunter_bot, and will interface you with our API! 🔥 🤘 \n" \
                      f"/start - Channel intro.\n" \
                      f"/menu - Show keyboard menu.\n" \
                      f"/register - Register with HostMonitor and receive a new API key.\n" \
                      f"/info - Get info about my apikey and my hosts.\n" \
                      f"/add <url> - Add url to the host monitor.\n" \
                      f"/hosts - Get hosts list.\n"

        bot.sendMessage(chat_id=chat_id, text=bot_message, reply_markup=main_keyboard)
        check_registered = bool(BotLink.query.filter_by(chat_id=chat_id).first())
        if not check_registered:
            bot.sendMessage(chat_id=chat_id, text=f"Looks like this is your first time there.\n"
                                                  f"Welcome to the club! 😼 🐦 🦇 \n")
            bot.send_chat_action(chat_id=chat_id, action="typing")
            bot_message_pre = f"Requesting new API ✈ ⏰...\n"
            bot.sendMessage(chat_id=chat_id, text=bot_message_pre)
            new_api = APINew(chat_id=chat_id)
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

    elif text == "/register" or text == "/start":
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

    elif text == "/info":
        bot.send_chat_action(chat_id=chat_id, action="typing")
        new_api_request = API(chat_id=chat_id)
        api_request = new_api_request.get_apikey_info()
        host_list = api_request.json()['hosts']
        host_list_format = str()
        for host in host_list:
            host_list_format += chr(10) + 'Host id: ' + str(host['id']) + chr(10) + 'Muted: ' + \
                                str(host['muted']) + chr(10) + 'URL: ' + host['url'] + chr(10)

        bot_message = f"Email: {api_request.json()['email'] if api_request.json()['email'] is not None else 'not linked'}\n" \
                      f"Total hosts added: {len(host_list)}\n" \
                      f"{host_list_format}" \
            if len(host_list) > 0 \
            else f"Add some hosts to watch! 👽\n"
        bot.sendMessage(chat_id=chat_id, text=bot_message, disable_web_page_preview=True)

    elif text == "/hosts":
        host_api_request = APIHost(chat_id=chat_id)
        api_request = host_api_request.get_all()
        hosts = []
        for index, host in enumerate(api_request.json()):
            host_callback = {
                "action": "get_host",
                "hostid": host['id'],
            }
            hosts.append(
                [telegram.InlineKeyboardButton(text=f"{host['url']}", callback_data=json.dumps(host_callback))])
        keyboard = telegram.InlineKeyboardMarkup(hosts, resize_keyboard=True)
        bot.sendMessage(chat_id=chat_id, text="Chose a host.", reply_markup=keyboard)
