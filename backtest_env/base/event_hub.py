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
        self.subscriptions = []

    def emit_to_frontend(self, event, data):
        self.sio.emit(event, data) if self.sio else None

    def emit(self, event, data):
        self.event_bus.publish(event, data)

    def subscribe(self, event_name: str, handler):
        self.subscriptions.append(self.event_bus.subscribe(event_name, handler))

    def unsubscribe(self):
        for unsubscribe in self.subscriptions:
            unsubscribe()
