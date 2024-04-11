import os
import socket

from flask import Flask
from flask_image_alchemy.storages import S3Storage
from flask_login import LoginManager
from flask_socketio import SocketIO
from modules.views import views_bp
from modules.items import items_bp
from modules.login import login_bp
from modules.classes import db


app = Flask(__name__)  # создание экземпляра приложения
sio = SocketIO(app, cors_allowed_origins='*')
storage = S3Storage()  # создание экземпляра хранилища изображений
storage.init_app(app)

# конфигурация приложения
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'  # назначение пути к базе данных
app.config['SECRET_KEY'] = 'TSSiteFlask'  # секретный ключ приложения
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # отключение предупреждений о модификации путей

# настройки для S3-хранилища
app.config['AWS_ACCESS_KEY_ID'] = os.environ.get('AWS_ACCESS_KEY_ID')
app.config['AWS_SECRET_ACCESS_KEY'] = os.environ.get('AWS_SECRET_ACCESS_KEY')
app.config['AWS_REGION_NAME'] = os.environ.get('AWS_REGION_NAME', 'eu-central-1')
app.config['S3_BUCKET_NAME'] = os.environ.get('AWS_REGION_NAME', 'haraka-local')
app.config["MEDIA_PATH"] = "/static/pic/avatars"

# конфигурация oauth провайдеров
app.config['OAUTH2_PROVIDERS'] = {
    'telegram': {
        'client_id': "6266128295",
        'client_secret': 'AAHmsbw16Cm11NtgDtZ_NZShdupIRWhw_Hw',
        'authorize_url': 'https://oauth.telegram.org/authorize',
        'token_url': 'https://oauth.telegram.com/access_token',
        'userinfo': {
            'url': 'https://api.github.com/user/emails',
        },
        'scopes': [],
    },

    # https://dev.vk.com/api/access-token/implicit-flow-user
    'vk': {
        'client_id': '51679319',
        'client_secret': 'URCsP1omgcBo0XRiBl5J',
        'authorize_url': 'https://oauth.vk.com/authorize',
        'token_url': 'https://oauth.vk.com/access_token',
        'userinfo': {
            'url': 'https://oauth.vk.com/blank.html',
        },
        'scopes': ['email'],
    },
}

lm = LoginManager(app)  # создание экземпляра логин-менеджера

sio = SocketIO(app, cors_allowed_origins='*')  # создание экземпляра socket.io

db.init_app(app)  # создание экземпляра базы данных
# current_page = "/"


app.register_blueprint(views_bp.module)
app.register_blueprint(items_bp.module)
app.register_blueprint(login_bp.module)




if __name__ == "__main__":
    # для захода на сайт с локальных устройств нужно задать ip адрес как у компьютера, получаем его
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    if ip:
        app.run(host=ip, port=5000, debug=True, threaded=True)
    else:
        app.run(host="192.168.3.2", port=5000, debug=True, threaded=True)
