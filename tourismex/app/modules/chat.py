# обработка SocketIO сообщений (еще не доработано)
import datetime

from flask import Blueprint
from flask_socketio import send

from ORM import ChatMessage


module = Blueprint('entity', __name__, url_prefix='/entity')


@sio.on('message')
def handle_message(data):
    print(f"Message: {data}")
    send(data, broadcast=True)

    message = ChatMessage(username=data['username'],
                          replay=None, message=data['message'],
                          sended=datetime.datetime.now(), attachment=None)
    db.session.add(message)
    db.session.commit()

