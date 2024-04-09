import datetime
import os
import socket

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
from flask_socketio import SocketIO, send
from flask_csp.csp import csp_header

app = Flask(__name__)  # создание экземпляра приложения

# конфигурация приложения: путь к базе данных, ключ шифрования и отключение отслеживания модификаций БД
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SECRET_KEY'] = 'TSSiteFlask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# настройки для S3-хранилища: ключ, секретный ключ, регион и название бакета
app.config['AWS_ACCESS_KEY_ID'] = os.environ.get('AWS_ACCESS_KEY_ID')
app.config['AWS_SECRET_ACCESS_KEY'] = os.environ.get('AWS_SECRET_ACCESS_KEY')
app.config['AWS_REGION_NAME'] = os.environ.get('AWS_REGION_NAME', 'eu-central-1')
app.config['S3_BUCKET_NAME'] = os.environ.get('AWS_REGION_NAME', 'haraka-local')

# путь для хранения изображений
app.config["MEDIA_PATH"] = "/static/pic/avatars"

# конфигурация oauth провайдеров
app.config['OAUTH2_PROVIDERS'] = {
    # Telegram: ID, Secret, URL для авторизации, URL для получения токена, URL для получения информации о пользователе
    'telegram': {
        'client_id': "6266128295",
        'client_secret': 'AAHmsbw16Cm11NtgDtZ_NZShdupIRWhw_Hw',
        'authorize_url': 'https://oauth.telegram.org/authorize',
        'token_url': 'https://oauth.telegram.com/access_token',
        'userinfo': {
            'url': 'api.telegram.org/bot6266128295:AAHmsbw16Cm11NtgDtZ_NZShdupIRWhw_Hw/getMe',
        },
        'scopes': [],
    },

    # https://dev.vk.com/api/access-token/implicit-flow-user
    # VK: ID, Secret, URL для авторизации, URL для получения токена, URL для получения информации о пользователе,
    # получаемые данные из JSON ответа
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

# создание экземпляров базы данных, логин-менеджера, хранилища S3 и SocketIO
db = SQLAlchemy(app)
lm = LoginManager(app)
storage = S3Storage()
storage.init_app(app)
sio = SocketIO(app, cors_allowed_origins='*')


# модель товара: ID, название, ссылка, цена, материал, описание
class Item(db.Model):
    item_id = db.Column(Integer, primary_key=True)
    item_name = db.Column(String(52), nullable=False)
    link = db.Column(String(100), nullable=False)
    price = db.Column(Float)
    material = db.Column(String(30))
    desc = db.Column(Text)


# модель пользователя: ID БД, Telegram ID, VK ID, тип пользователя, наложеннные ограничения, никнейм, почта, аватар,
# дата рождения, о себе, город проживания
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


# модель сообщения: ID, ID автора, имя автора, ID ответа, текст сообщения, время отправки, вложения
class ChatMessage(db.Model):
    message_id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer)
    username = db.Column(String(64))
    replay = db.Column(Integer)
    message = db.Column(Text)
    sended = db.Column(db.DateTime)
    attachment = db.Column(
        StdImageField(
        )
    )


# вход пользователя в систему через логин-менеджер
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# блок маршрутизации приложения
#
#
@app.route('/')
@csp_header({
    'default-src': "'self' 'unsafe-inline' api-maps.yandex.ru yandex.ru oauth.telegram.org telegram.org",
    'script-src': "'self' 'unsafe-eval' yandex.ru oauth.telegram.org telegram.org",
    'script-src-elem': "'self' api-maps.yandex.ru oauth.telegram.org telegram.org",
    'frame-ancestors': "oauth.telegram.org telegram.org"
})
# стартовая страница
def index():
    db.create_all()
    return render_template("inx.html")


# страница транспорта
@app.route('/transport')
def transport():
    return render_template("transport.html")


# страница о климате области
@app.route('/climate')
def climate():
    return render_template("climate.html")


# страница об истории края
@app.route('/history')
def history():
    return render_template("history.html")


# страница о местах отдыха
@app.route('/rest_places')
def rest_places():
    return render_template("rest_places.html")


# страница о сопредельных регионах
@app.route('/neighbours')
def neighbours():
    return render_template("neighbours.html")


# страница с интерактивной картой
@app.route('/svg_map')
def svg_map():
    print("svg_map")
    return render_template("svg_map.html")


# обработка запросов по товарам
@app.route('/goods', methods=['POST', 'GET'])
def item_processing():
    # при отправке данных из формы: отправление данных в БД, редактирование и удаление товара
    if request.method == 'POST':
        if request.form.get('send') == 'Отправить':

            # заполнение согласно классу Item
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

            except Exception:
                return "Произошла ошибка добавления предмета. Свяжитесь с администратором."

        elif request.form.get('delete') == 'Удалить':
            # попытка получения товара по ID, при неудаче выводится 404 код
            item = Item.query.get_or_404(request.form['item_id'])

            # удаление из БД
            try:
                db.session.delete(item)
                db.session.commit()
                return redirect('/goods')
            except:
                return "Ошибка при удалении"

        elif request.form.get('edit') == 'Редактировать':
            # попытка получения товара по ID, при неудаче выводится 404 код
            item = Item.query.get_or_404(request.form['item_id'])

            # получение данных из непустых форм и запись в БД согласно классу Item
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

    # при GET запросе вывод списка всех предметов
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


# выход из профиля
@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


# отображение страницы управления профилем
@login_required
@app.route('/user_account', methods=['POST', 'GET'])
def account_edit():
    return render_template("user_account.html", user=current_user)


# авторизация OAuth2
# функция принимает имя провайдера, которе влияет на нюансы работы авторизации каждого отдельного провайдера
# можно легко масштабировать на других провайдеров, кроме тех, что используют первую версию OAuth
@app.route('/authorize/<provider>')
def oauth2_authorize(provider):
    # если пользователь уже авторизован
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    # получение данных о провайдере и выход из функции, если данные пустые
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

    # переадресация на созданный URL ("?" является стандатрным разделителем в параметрах URL)
    return redirect(provider_data['authorize_url'] + '?' + qs)


# обработка callback
# функция принимает имя провайдера
@app.route('/callback/<provider>')
def oauth2_callback(provider):
    # если пользователь уже авторизован, то все готово
    if not current_user.is_anonymous:
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
    # изъян: никнейм может повториться (а должен быть уникальным), и возникнет ошибка регистрации
    user = db.session.scalar(db.select(User).where(User.email == email))
    if user is None:
        user = User(email=email, nickname=email.split('@')[0], user_type=1, vk_id=vk_id if provider == 'vk' else None,
                    telegram_id=telegram_id if provider == 'telegram' else None)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return render_template("user_account.html", user=user)


# запуск главного приложения
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
