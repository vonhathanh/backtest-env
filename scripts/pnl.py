from backtest_env.order_manager import OrderManager
from backtest_env.position_manager import PositionManager
from backtest_env.utils import create_long_order, create_short_order


position_manager = PositionManager(10000)
order_manager = OrderManager(position_manager, None)

first_order = create_long_order(price=100.0, quantity=1.0)

order_manager.add_order(first_order)
order_manager.process_orders()

orders = []
for i in range(1, 11):
    orders.append(create_short_order(quantity=0.1, price=100 - i))
order_manager.add_orders(orders)
order_manager.process_orders()

print(position_manager.get_unrealized_pnl(50))
