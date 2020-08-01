from flask import Flask

from flask_cors import CORS
from flask_migrate import Migrate

from flask_restx import Api
from apps.bot.views import api as bot_namespace
from apps.extensions import db
from config import Settings
settings = Settings()


def create_app():
    # Init Flask create_app
    new_app = Flask(__name__)
    new_app.config.from_object(settings)
    register_ext(new_app)
    CORS(new_app, resources={r"/bot/*": {"origins": "*"}})
    migrate = Migrate(db=db)
    migrate.init_app(app=new_app)

    api = Api(title='Telegram Bot API', version='1.0.0',
              description='Telegram bot',
              )

    api.add_namespace(bot_namespace)
    api.init_app(app=new_app)

    return new_app


# Register extensions
def register_ext(new_app):
    db.init_app(new_app)
