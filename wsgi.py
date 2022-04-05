from app import app, socketio
from flask_socketio import SocketIO

if __name__ == '__main__':
    from gevent import monkey
    monkey.patch_all()
    socketio.run(app, debug=True, port=8888, threaded=True)
