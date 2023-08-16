import datetime
import os
from flask import Flask, Response, render_template, request, redirect, flash, url_for, current_app, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from flask_socketio import SocketIO, send
import requests
import secrets
from urllib.parse import urlencode
from flask_image_alchemy.storages import S3Storage
from flask_image_alchemy.fields import StdImageField
from flask_csp.csp import csp_header


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SECRET_KEY'] = 'TSSiteFlask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['OAUTH2_PROVIDERS'] = {
    'telegram': {
        'client_id': "6266128295",
        'client_secret': 'AAHmsbw16Cm11NtgDtZ_NZShdupIRWhw_Hw',
        'authorize_url': 'https://oauth.telegram.org/authorize',
        'token_url': 'https://oauth.telegram.com/access_token',
        'userinfo': {
            'url': 'https://api.github.com/user/emails',
            'email': lambda json: json['email']
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
            'email': lambda json: json[0]['email']
        },
        'scopes': ['email'],
    },
}

db = SQLAlchemy(app)
lm = LoginManager(app)
sio = SocketIO(app, cors_allowed_origins='*')


app.config['AWS_ACCESS_KEY_ID'] = os.environ.get('AWS_ACCESS_KEY_ID')
app.config['AWS_SECRET_ACCESS_KEY'] = os.environ.get('AWS_SECRET_ACCESS_KEY')
app.config['AWS_REGION_NAME'] = os.environ.get('AWS_REGION_NAME', 'eu-central-1')
app.config['S3_BUCKET_NAME'] = os.environ.get('AWS_REGION_NAME', 'haraka-local')

if __name__ == "main":
    sio.run(app)


class Item(db.Model):
    item_id = db.Column(Integer, primary_key=True)
    item_name = db.Column(String(52), nullable=False)
    link = db.Column(String(100), nullable=False)
    price = db.Column(Float)
    material = db.Column(String(30))
    desc = db.Column(Text)


class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(64), nullable=True, unique=True)
    vk_id = db.Column(db.String(64), nullable=True, unique=True)
    user_type = db.Column(db.SmallInteger, nullable=False)
    restriction = db.Column(db.Integer, nullable=True)
    nickname = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=True, unique=True)
    image = db.Column(StdImageField(storage=S3Storage(
    )))
    birth_date = db.Column(db.Date, nullable=True)
    about = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(64), nullable=True)


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


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/index')
@app.route('/')
@csp_header({
    'default-src': "'self' 'unsafe-inline' api-maps.yandex.ru yandex.ru oauth.telegram.org telegram.org",
    'script-src': "'self' 'unsafe-eval' yandex.ru oauth.telegram.org telegram.org",
    'script-src-elem': "'self' api-maps.yandex.ru oauth.telegram.org telegram.org",
    'frame-ancestors': "oauth.telegram.org telegram.org"
})
def index():
    return render_template("inx.html")


@app.route('/index')
@app.route('/')
def responsing():
    response = Response()
    response.headers['Content-Security-Policy'] = "frame-ancestors oauth.telegram.org telegram.org"
    return response


@app.route('/start')
def start():
    return render_template("index.html")


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


@app.route('/goods', methods=['POST', 'GET'])
def item_processing():
    print("item_processing")
    if request.method == 'POST':
        print("post")
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


@app.route('/user_account', methods=['POST', 'GET'])
def account_edit():
    return render_template("user_account.html")


@app.route('/authorize/<provider>')
def oauth2_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # генерация строки информационного шума
    session['oauth2_state'] = secrets.token_urlsafe(16)

    # создание строки URL для авторизации
    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('oauth2_callback', provider=provider,
                                _external=True),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    })
    print(url_for('oauth2_callback', provider=provider,
                                _external=True))

    # переадресация на созданный URL
    return redirect(provider_data['authorize_url'] + '?' + qs)


@app.route('/callback/<provider>')
def oauth2_callback(provider):
    print("callback")
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # обработка ошибки аутентификации - редирект на 'index'
    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}')
        return redirect(url_for('index'))

    if request.args['state'] != session.get('oauth2_state'):
        abort(401)

    if 'code' not in request.args:
        abort(401)

    # exchange the authorization code for an access token
    response = requests.post(provider_data['token_url'], data={
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('oauth2_callback', provider=provider,
                                _external=True),
    }, headers={'Accept': 'application/json'})
    if response.status_code != 200:
        abort(401)
    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        abort(401)

    # use the access token to get the user's email address
    response = requests.get(provider_data['userinfo']['url'], headers={
        'Authorization': 'Bearer ' + oauth2_token,
        'Accept': 'application/json',
    })
    if response.status_code != 200:
        abort(401)
    print(provider_data)
    email = provider_data['email'](response.json())

    # find or create the user in the database
    user = db.session.scalar(db.select(User).where(User.email == email))
    if user is None:
        user = User(email=email, username = email.split('@')[0] if email == None else "New User")
        db.session.add(user)
        db.session.commit()

    # log the user in
    login_user(user)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(host='192.168.3.2', port=5000, debug=True, threaded=False)
