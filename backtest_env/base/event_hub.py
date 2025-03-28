from eventure import EventBus, EventLog
from socketio import Client

event_bus = EventBus(EventLog())


class EventHub:
    """
    regular event will be handled by components in our system
    socketio_event will be handled by Front-end
    """

    def __init__(self, sio: Client = None):
        self.sio = sio
        self.event_bus = event_bus

    def emit_to_frontend(self, event, data):
        self.sio.emit(event, data) if self.sio else None

    def emit(self, event, data):
        self.event_bus.publish(event, data)
