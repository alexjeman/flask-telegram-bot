import sys
import telegram
from flask import request
from flask_restx import Resource
import json
from apps.bot.namespace import api
from apps.bot.conversations import conversation_handler
from apps.bot.callbacks import callback_handler
from config import Settings

settings = Settings()
bot = telegram.Bot(settings.BOT_TOKEN)


@api.route('/', methods=['POST'], doc=False)
class BotResource(Resource):
    @api.doc("bot_root")
    def post(self):
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        try:
            is_callback = bool(update.callback_query.data)
        except AttributeError as error:
            print("Possible spam callback received:", update, file=sys.stderr)
            is_callback = False

        try:
            is_chat_message = bool(update.message)
        except AttributeError as error:
            print("Possible spam message received:", update, file=sys.stderr)
            is_chat_message = False

        if is_chat_message:
            print("Incoming chat message:", update.message, file=sys.stderr)
            chat_id = update.message.chat_id
            message_response = conversation_handler(bot=bot, chat_id=chat_id, update=update)
            if message_response:
                bot.sendMessage(chat_id=chat_id, text=message_response)
        elif is_callback:
            print("Incoming callback message:", update.callback_query.data, file=sys.stderr)
            chat_id = update.callback_query.message.chat.id
            callback_response = callback_handler(bot=bot, chat_id=chat_id, query=update.callback_query)
            if callback_response:
                bot.sendMessage(chat_id=chat_id, text=callback_response)


@api.route("/setwebhook", methods=['GET'], doc=False)
class BotResource(Resource):
    @api.doc("webhook")
    def get(self):
        s = bot.setWebhook('{URL}'.format(URL=settings.BOT_URL))
        if s:
            return 'webhook set'
        else:
            return 'webhook failed'


@api.route("/notifications", methods=['POST'], doc=False)
class BotResource(Resource):
    @api.doc("webhook")
    def post(self):
        btn_unmute = {
            "action": "mute",
            "hostid": request.json['host_id'],
            "muted": False
        }
        btn_mute = {
            "action": "mute",
            "hostid": request.json["host_id"],
            "muted": True
        }
        buttons = [[
            telegram.InlineKeyboardButton(text="Mute", callback_data=json.dumps(btn_mute)),
            telegram.InlineKeyboardButton(text="Unmute", callback_data=json.dumps(btn_unmute))
        ]]
        keyboard = telegram.InlineKeyboardMarkup(buttons)
        bot.send_chat_action(chat_id=request.json['chat_id'], action="typing")
        bot.sendMessage(chat_id=request.json['chat_id'], text=request.json['text'], reply_markup=keyboard)
