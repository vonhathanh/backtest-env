from time import time_ns
from socketio import Client

class Event:
    def __init__(self, data: any):
        self.data = data
        # Use time_ns() to avoid the precision loss caused by the float type.
        # divide by 1 million to get millisecond
        # use floor division to avoid the risk of being in the future
        self.timestamp = time_ns() // 1_000_000

class EventBus:
    def __init__(self):
        self.handlers: dict[str, list[callable]] = {}

    def subscribe(self, event_name: str, handler: callable):

        handlers = self.handlers.setdefault(event_name, [])
        handlers.append(handler)
        return event_name, handler
    
    def unsubcribe(self, subscription: tuple[str, callable]):
        event_name, handler = subscription
        handlers = self.handlers.setdefault(event_name, [])
        handlers = [h for h in handlers if h != handler]

    def publish(self, event_name: str, data: any):
        handlers = self.handlers.get(event_name, [])
        for fn in handlers:
            fn(Event(data))


event_bus = EventBus()


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

    def subscribe(self, event_name: str, handler: callable):
        self.subscriptions.append(self.event_bus.subscribe(event_name, handler))

    def unsubscribe(self):
        for subscrition in self.subscriptions:
            self.event_bus.unsubcribe(subscrition)
