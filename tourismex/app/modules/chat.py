from tourismex.app.modules.classes import db, ChatMessage
from tourismex.app.app import sio
# обработка SocketIO сообщений (еще не доработано)
import datetime

from flask_socketio import send, SocketIO



@sio.on('message')
def handle_message(data):
    print(f"Message: {data}")
    send(data, broadcast=True)

    message = ChatMessage(username=data['username'],
                          replay=None, message=data['message'],
                          sended=datetime.datetime.now(), attachment=None)
    db.session.add(message)
    db.session.commit()

