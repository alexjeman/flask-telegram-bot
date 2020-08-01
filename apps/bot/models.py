from apps.extensions import db


class BotLink(db.Model):
    __tablename__ = 'botlink'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, unique=True, nullable=False)
    chat_id = db.Column(db.Integer, unique=True, nullable=True)

    def __init__(self, key, chat_id):
        self.key = key
        self.chat_id = chat_id
