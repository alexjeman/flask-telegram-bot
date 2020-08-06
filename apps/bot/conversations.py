import json

from apps.bot.api_requests import API, APINew, APILink, APIHost
from apps.bot.models import BotLink, db
import telegram


def conversation_handler(bot, chat_id, update):
    text = getattr(update.message, 'text', str()).encode('utf-8').decode()

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
        """Splits url_1 url_2 url_3 from text and sends requests to check and add each of them"""
        bot.send_chat_action(chat_id=chat_id, action="typing")
        _, *parsed_host = text.split()
        for url in parsed_host:
            new_host = APIHost(chat_id=chat_id, callback_json=url)
            api_response = new_host.add_host()
            response = api_response.json()
            if f"{api_response.status_code}" == "201":
                api_response_format = f"Host id: {response.get('id')}\n" \
                                      f"Muted: {response.get('muted')}\n" \
                                      f"URL: {response.get('url')}\n"

                bot.sendMessage(chat_id=chat_id, text=api_response_format, disable_web_page_preview=True)
            elif f"{api_response.status_code}" == "400":
                bot.sendMessage(chat_id=chat_id, text=response['message'])

    elif text == "/add":
        bot.send_chat_action(chat_id=chat_id, action="typing")
        bot.sendMessage(chat_id=chat_id, text="Usage example, type in chat: /add https://www.google.com/")

    elif text == "/menu":
        bot.sendMessage(chat_id=chat_id, text="Select from the menu.", reply_markup=main_keyboard)

    elif text == "/start":
        bot.send_chat_action(chat_id=chat_id, action="typing")
        bot_message = f"Welcome to HostMonitor,\n" \
                      f"I'm HostHunter_bot, and will interface you with our API! 🔥 🤘 \n" \
                      f"/start - Channel intro. 🏮\n" \
                      f"/menu - Show keyboard menu. ⌨\n" \
                      f"/register - Register with HostMonitor and receive a new API key. 🔑\n" \
                      f"/info - Get info about my apikey. 💡\n" \
                      f"/add <url> - Add url to the host monitor. 🔗\n" \
                      f"/hosts - Get hosts list. 🖇\n"

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
            response = new_api_request.json()
            if f"{new_api_request.status_code}" == "200":
                bot_message_success = f"Your new personal API key is : {response['apikey']}\n"
                bot.sendMessage(chat_id=chat_id, text=bot_message_success)
                new_botlink = BotLink(
                    key=response['apikey'],
                    chat_id=chat_id
                )
                db.session.add(new_botlink)
                db.session.commit()
                print("linked", chat_id, response['apikey'])

    elif text == "/register" or text == "/start":
        bot.send_chat_action(chat_id=chat_id, action="typing")
        new_api = APINew(chat_id=chat_id)
        bot_message_pre = f"Requesting new API ✈ ⏰...\n"
        bot.sendMessage(chat_id=chat_id, text=bot_message_pre)

        new_api_request = new_api.get_newkey()
        response = new_api_request.json()
        if f"{new_api_request.status_code}" == "200":
            bot_message_success = f"Your new personal API key is : {response['apikey']}\n"
            bot.sendMessage(chat_id=chat_id, text=bot_message_success)
            new_botlink = BotLink(
                key=response['apikey'],
                chat_id=chat_id
            )
            db.session.add(new_botlink)
            db.session.commit()
            print("linked", chat_id, response['apikey'])

        elif f"{new_api_request.status_code}" == "409":
            bot.sendMessage(chat_id=chat_id, text=f"You are already registered, try some get requests! 🔔\n")

    elif text == "/info":
        bot.send_chat_action(chat_id=chat_id, action="typing")
        new_api_request = API(chat_id=chat_id)
        api_request = new_api_request.get_apikey_info()
        host_list = api_request.json()
        host_list_format = str()
        for host in host_list['hosts']:
            host_list_format += f"Host id: {host['id']}\n" \
                                f"Muted: {host['muted']}\n" \
                                f"URL: {host['url']}\n"

        bot_message = f"Email: {host_list['email'] if host_list['email'] is not None else 'not linked'}\n" \
                      f"Total hosts added: {len(host_list['hosts'])}\n" \
                      f"Try /hosts for the full host list ⤵" \
            if len(host_list['hosts']) > 0 \
            else f"Add some hosts to watch! 👽 /add\n"
        bot.sendMessage(chat_id=chat_id, text=bot_message, disable_web_page_preview=True)

    elif text == "/hosts":
        host_api_request = APIHost(chat_id=chat_id)
        api_request = host_api_request.get_all()
        response = api_request.json()
        hosts = []
        for index, host in enumerate(response):
            btn_unmute = {
                "action": "mute",
                "hostid": host['id'],
                "muted": False
            }
            btn_mute = {
                "action": "mute",
                "hostid": host['id'],
                "muted": True
            }
            btn_delete = {
                "action": "delete",
                "hostid": host['id']
            }
            host_callback = {
                "action": "get_host",
                "hostid": host['id'],
            }
            hosts.append(
                [telegram.InlineKeyboardButton(text=f"📂 {host['url']}", callback_data=json.dumps(host_callback))])
            hosts.append([
                telegram.InlineKeyboardButton(text="Mute", callback_data=json.dumps(btn_mute)),
                telegram.InlineKeyboardButton(text="Unmute", callback_data=json.dumps(btn_unmute)),
                telegram.InlineKeyboardButton(text="Delete", callback_data=json.dumps(btn_delete))
            ])
        keyboard = telegram.InlineKeyboardMarkup(hosts, resize_keyboard=True)
        bot.sendMessage(chat_id=chat_id,
                        text="Click on the icon 📂 to view detailed logs ⤵" if len(hosts) > 0
                        else "Add some hosts to watch first! 🔭 /add",
                        reply_markup=keyboard)
