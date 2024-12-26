class OrderDispatcher:
    # send orders to the environment/engine
    # normally, we use GET request to submit order but in simulation we don't have to do that
    @staticmethod
    def dispatch(orders: list, target):
        target.add_orders(orders)