from tourismex.app.modules.classes import get_db
from flask import render_template, request, redirect, flash, url_for, current_app, session, abort, Blueprint

from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import requests
import secrets
from urllib.parse import urlencode
from extensions import init_extensions
from flask_image_alchemy.fields import StdImageField
from flask_login import UserMixin


login_bp = Blueprint('entity', __name__, url_prefix='/entity')


def get_user_model(db):

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
                storage=init_extensions()[1],
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

    return User


# авторизация OAuth2
@login_bp.route('/authorize/<provider>')
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
@login_bp.route('/callback/<provider>')
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

    db = get_db()
    user_model = get_user_model(db)
    user = db.session.scalar(db.select(user_model).where(user_model.email == email))
    if user is None:
        user = user_model(email=email, nickname=email.split('@')[0], user_type=1, vk_id=vk_id if provider == 'vk' else None,
                          telegram_id=telegram_id if provider == 'telegram' else None)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return render_template("user_account.html", user=user)