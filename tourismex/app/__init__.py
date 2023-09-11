import os

from flask import Flask
from .database import db
from flask_login import LoginManager
from flask_socketio import SocketIO


def create_app():
    app = Flask(__name__)  # создание экземпляра приложения

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
    with app.test_request_context():
        db.create_all()
    # current_page = "/"

    import app.modules.views as views
    import app.modules.items as items
    import app.modules.ORM as ORM
    import app.modules.login as login
    import app.modules.chat as chat

    app.register_blueprint(views.module)
    app.register_blueprint(items.module)
    app.register_blueprint(ORM.module)
    app.register_blueprint(login.module)
    app.register_blueprint(chat.module)

    #    app.run(host='192.168.3.2', port=5000, debug=True, threaded=False)
    return app
