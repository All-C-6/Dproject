import datetime
import os

from flask import Flask, Response, render_template, request, redirect, flash, url_for, current_app, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.event import listen
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import requests
import secrets
from urllib.parse import urlencode
from flask_image_alchemy.storages import S3Storage
from flask_image_alchemy.fields import StdImageField
from flask_image_alchemy.events import before_update_delete_callback, before_delete_delete_callback
from flask_socketio import SocketIO, send
from flask_csp.csp import csp_header

# конфигурация приложения
app = Flask(__name__)  # создание экземпляра приложения
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

db = SQLAlchemy(app)  # создание экземпляра базы данных
lm = LoginManager(app)  # создание экземпляра логин-менеджера
storage = S3Storage()  # создание экземпляра хранилища изображений
storage.init_app(app)
sio = SocketIO(app, cors_allowed_origins='*')
current_page = "/"


if __name__ == "main":
    sio.run(app)


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


# логин-менеджер
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# получение текущей страницы пользователя (еще не реализовано)
@app.before_request
def store_current_page():
    global current_page
    current_page = request.path


# маршрутизация
@app.route('/')
@csp_header({
    'default-src': "'self' 'unsafe-inline' api-maps.yandex.ru yandex.ru oauth.telegram.org telegram.org",
    'script-src': "'self' 'unsafe-eval' yandex.ru oauth.telegram.org telegram.org",
    'script-src-elem': "'self' api-maps.yandex.ru oauth.telegram.org telegram.org",
    'frame-ancestors': "oauth.telegram.org telegram.org"
})
def index():
    return render_template("inx.html")


@app.route('/transport')
def transport():
    return render_template("transport.html")


@app.route('/climate')
def climate():
    return render_template("climate.html")


@app.route('/history')
def history():
    return render_template("history.html")


@app.route('/rest_places')
def rest_places():
    return render_template("rest_places.html")


@app.route('/neighbours')
def neighbours():
    return render_template("neighbours.html")


@app.route('/svg_map')
def svg_map():
    print("svg_map")
    return render_template("svg_map.html")


# обработка запросов по товарам
@app.route('/goods', methods=['POST', 'GET'])
def item_processing():
    if request.method == 'POST':
        if request.form.get('send') == 'Отправить':
            print("send")
            item_name = str(request.form['item_name'])
            link = str(request.form['link'])
            price = int(request.form['price'])
            material = request.form['material']
            desc = str(request.form['description'])

            item = Item(item_name=item_name, link=link, price=price, material=material, desc=desc)

            try:
                db.session.add(item)
                db.session.commit()
                return redirect('/goods')
            except:
                return "Произошла ошибка добавления предмета. Свяжитесь с администратором."

        elif request.form.get('delete') == 'Удалить':
            item = Item.query.get_or_404(request.form['item_id'])

            try:
                db.session.delete(item)
                db.session.commit()
                return redirect('/goods')
            except:
                return "Ошибка при удалении"

        elif request.form.get('edit') == 'Редактировать':
            item = Item.query.get_or_404(request.form['item_id'])
            if request.form['item_name'] != "":
                item.item_name = str(request.form['item_name'])
            if request.form['link'] != "":
                item.link = str(request.form['link'])
            if request.form['price'] != "":
                item.link = int(request.form['price'])
            if request.form['material'] != "":
                item.material = request.form['material']
            if request.form['description'] != "":
                item.desc = str(request.form['description'])

            db.session.commit()
            return redirect('/goods')

    else:
        items = Item.query.order_by(Item.price).all()
        return render_template("items.html", items=items)


# обработка SocketIO сообщений (еще не доработано)
@sio.on('message')
def handle_message(data):
    print(f"Message: {data}")
    send(data, broadcast=True)

    message = ChatMessage(username=data['username'],
                          replay=None, message=data['message'],
                          sended=datetime.datetime.now(), attachment=None)
    db.session.add(message)
    db.session.commit()


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


# управление профилем
@login_required
@app.route('/user_account', methods=['POST', 'GET'])
def account_edit():
    return render_template("user_account.html", user=current_user)


# авторизация OAuth2
@app.route('/authorize/<provider>')
def oauth2_authorize(provider):
    if not current_user.is_anonymous:  # если пользователь уже авторизован
        return redirect(url_for('index'))

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)  # получение данных о провайдере
    if provider_data is None:
        abort(404)

    # генерация строки информационного шума
    session['oauth2_state'] = secrets.token_urlsafe(16)
    # page = request.url
    # print(page)
    # создание строки URL для авторизации
    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('oauth2_callback', provider=provider,
                                _external=True),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    })

    # переадресация на созданный URL
    return redirect(provider_data['authorize_url'] + '?' + qs)


# обработка callback
@app.route('/callback/<provider>')
def oauth2_callback(provider):
    # print("callback")
    if not current_user.is_anonymous:  # если пользователь уже авторизован, то все готово
        return redirect(url_for('index'))

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)  # получение данных о провайдере
    if provider_data is None:
        abort(404)

    # обработка ошибки аутентификации - редирект на главную страницу
    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}')
        return redirect(url_for('index'))

    # проверка состояния запроса и кода ответа
    if request.args['state'] != session.get('oauth2_state'):
        abort(401)

    if 'code' not in request.args:
        abort(401)

    # получение токена
    response = requests.post(provider_data['token_url'], data={
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('oauth2_callback', provider=provider,
                                _external=True),
    }, headers={'Accept': 'application/json'})
    # print(f"Содержание (строка): {response.text}")
    # print(f"Содержание: {data['email']}")
    # print(type(data))
    if response.status_code != 200:  # если код ответа не 200, то прервать
        abort(401)

    # парсинг ответа JSON (в процессе доработки)
    data = response.json()
    oauth2_token = response.json().get('access_token')
    if not oauth2_token or response.status_code != 200:
        abort(401)

    email = data['email']
    if provider == 'vk':
        vk_id = data["user_id"]

    if provider == 'telegram':
        telegram_id = data["user_id"]

    # создание нового и/или логин пользователя
    user = db.session.scalar(db.select(User).where(User.email == email))
    if user is None:
        user = User(email=email, nickname=email.split('@')[0], user_type=1, vk_id=vk_id if provider == 'vk' else None,
                    telegram_id=telegram_id if provider == 'telegram' else None)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return render_template("user_account.html", user=user)


if __name__ == "__main__":
    app.run(host='192.168.3.2', port=5000, debug=True, threaded=False)
