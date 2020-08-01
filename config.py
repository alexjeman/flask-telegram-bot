import os
from dotenv import load_dotenv
load_dotenv(verbose=True)


class Settings:
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BOT_URL = os.getenv("BOT_URL")
    API_URL = os.getenv("API_URL")
