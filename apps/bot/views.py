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

        is_edited = getattr(update, 'edited_message')
        is_callback = getattr(update, 'callback_query')
        is_chat_message = getattr(update, 'message')

        if is_callback is not True and is_chat_message is not True and is_edited is not True:
            print("Spam message:", is_callback, is_chat_message, is_edited, update, file=sys.stderr)

        if is_chat_message:
            print("Incoming chat message:", update.message.text, file=sys.stderr)
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
        host_id = request.json['host_id']
        chat_id = request.json['chat_id']
        text = request.json['text']
        btn_unmute = {
            "action": "mute",
            "hostid": host_id,
            "muted": False
        }
        btn_mute = {
            "action": "mute",
            "hostid": host_id,
            "muted": True
        }
        btn_delete = {
            "action": "delete",
            "hostid": host_id
        }
        buttons = []
        buttons.append([
            telegram.InlineKeyboardButton(text="Mute", callback_data=json.dumps(btn_mute)),
            telegram.InlineKeyboardButton(text="Unmute", callback_data=json.dumps(btn_unmute)),
            telegram.InlineKeyboardButton(text="Delete", callback_data=json.dumps(btn_delete))
        ])
        keyboard = telegram.InlineKeyboardMarkup(buttons)
        bot.send_chat_action(chat_id=chat_id, action="typing")
        bot.sendMessage(chat_id=chat_id, text=text, reply_markup=keyboard)
