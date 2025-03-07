from socketio import SimpleClient


class EventEmitter:
    def __init__(self, sio: SimpleClient = None):
        self.sio = sio

    def emit(self, event, data):
        self.sio.emit(event, data) if self.sio else None
