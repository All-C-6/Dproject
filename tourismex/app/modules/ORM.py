from flask import Blueprint
from flask_image_alchemy.fields import StdImageField
from flask_image_alchemy.storages import S3Storage
from flask_login import UserMixin

from sqlalchemy import Integer, String, Float, Text
from app.database import db

module = Blueprint('entity', __name__, url_prefix='/entity')
storage = S3Storage()  # создание экземпляра хранилища изображений
storage.init_app(module)


# модель товара
class Item(db.Model):
    item_id = db.Column(Integer, primary_key=True)
    item_name = db.Column(String(52), nullable=False)
    link = db.Column(String(100), nullable=False)
    price = db.Column(Float)
    material = db.Column(String(30))
    desc = db.Column(Text)


# модель пользователя
class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(64), nullable=True, unique=True)
    vk_id = db.Column(db.String(64), nullable=True, unique=True)
    user_type = db.Column(db.SmallInteger, nullable=False)
    restriction = db.Column(db.Integer, nullable=True)
    nickname = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=True, unique=True)
    avatar = db.Column(
        StdImageField(
            storage=storage,
            variations={
                'thumbnail': {"width": 200, "height": 200, "crop": True}
            }
        ), nullable=True
    )
    birth_date = db.Column(db.Date, nullable=True)
    about = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(64), nullable=True)

    def get_id(self):
        return self.user_id


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