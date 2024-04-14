from flask_image_alchemy.storages import S3Storage
from flask_socketio import SocketIO
from tourismex.app.app import app
from classes import db, Item, User, ChatMessage


def init_extensions():
    sio = SocketIO(app, cors_allowed_origins='*')
    storage = S3Storage()  # создание экземпляра хранилища изображений
    storage.init_app(app)

    return sio, storage, db, Item, User, ChatMessage
