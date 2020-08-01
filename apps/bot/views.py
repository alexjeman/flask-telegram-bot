import sys
import telegram
from flask import request
from flask_restx import Resource

from apps.bot.namespace import api
from apps.bot.conversations import conversation_handler
from config import Settings
settings = Settings()
bot = telegram.Bot(settings.BOT_TOKEN)


@api.route('/', methods=['POST'], doc=False)
class BotResource(Resource):
    @api.doc("bot_root")
    def post(self):
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        chat_id = update.message.chat_id
        print("Incoming chat message:", update.message, file=sys.stderr)
        response = conversation_handler(bot=bot, chat_id=chat_id, update=update)
        if response:
            bot.sendMessage(chat_id=chat_id, text=response)


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
        bot.send_chat_action(chat_id=request.json['chat_id'], action="typing")
        bot.sendMessage(chat_id=request.json['chat_id'], text=request.json['text'] + '/mute')
