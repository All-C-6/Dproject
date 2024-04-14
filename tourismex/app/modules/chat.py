
from tourismex.app.app import sio
# обработка SocketIO сообщений (еще не доработано)
import datetime

from flask_socketio import send, SocketIO
from tourismex.app.modules.extensions import init_extensions

db = init_extensions()[2]
ChatMessage = init_extensions()[5]


@sio.on('message')
def handle_message(data):
    print(f"Message: {data}")
    send(data, broadcast=True)

    message = ChatMessage(username=data['username'],
                          replay=None, message=data['message'],
                          sended=datetime.datetime.now(), attachment=None)
    db.session.add(message)
    db.session.commit()

