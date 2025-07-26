from eventure import EventBus, EventLog
from socketio import Client

event_bus = EventBus(EventLog())


class EventHub:
    # used to communicate between components in our system
    def __init__(self):
        self.event_bus = event_bus
        self.subscriptions = []

    def emit(self, event, data):
        self.event_bus.publish(event, data)

    def subscribe(self, event_name: str, handler):
        self.subscriptions.append(self.event_bus.subscribe(event_name, handler))

    def unsubscribe(self):
        for unsubscribe in self.subscriptions:
            unsubscribe()


class SocketIoEventHub:
    # used to communicate with external components (Front-end, chat system, Exchange API server)
    def __init__(self, sio: Client):
        self.sio = sio

    def emit(self, event, data):
        self.sio.emit(event, data)
