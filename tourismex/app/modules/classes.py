from extensions import init_extensions
from flask_image_alchemy.fields import StdImageField
from flask_login import UserMixin

from sqlalchemy import Integer, String, Float, Text
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # создание экземпляра базы данных


def get_db():
    return db


# модель сообщения
class ChatMessage(db.Model):
    message_id = db.Column(Integer, primary_key=True)
    username = db.Column(String(64))
    replay = db.Column(Integer)
    message = db.Column(Text)
    sended = db.Column(db.DateTime)
    attachment = db.Column(
        StdImageField(
        )
    )


