# backtest-env
- Act as API server, FE call request -> server creates a new back-test process and run with the input params

# Decision choices
- Use close price or open price when new candle arrives?
  - Close price: new candle -> fill open orders, submit new orders
  - Open price: new candle -> submit new orders, fill open orders
  - We'll use Close price because most of our strategies react based on previous candle

# Testing
- Run `python -m pytest` in root folder to run all unit tests
- Run `python -m pytest/file/directory` to run tests of single file
- Include `-s` to display logs

# Rules
- Submit orders: use close price of current candle
- Fill orders:
  - Market order: use close price
  - Limit/stop order: use order's price
- Close position:
  - Before update(): use close price
  - After update(): use close price
  - Default: close price
- PnL: use close price
- Every filepath string must relative with root directory (where this README is located)
- Realtime backtest progress update flow: 
  1. FE & BE connect on the same websocket server
  2. Loop
     2.1 BE wait for ack from FE
     2.2 BE load the latest candle
     2.3 BE act according that candle close price: submit orders, close positions
     2.4 BE send that candle, orders, positions to FE
     2.5 FE render according to data from BE
     2.6 FE send ack to BE

# Scripting
- Run `python -m scripts.your_script_name_without.py_extension` to run the script.
The reason is that python treats script as top-level module, it won't be able to find backtest_env.
We can add hacky methods like try catch, append sys.path, install this as a module using setup.py but I don't like them

# TODOs
- Add stop/pause button
- Add logging functionality: order history
- Hook to update orders, position automatically
- Order side should be in USD, not asset quantity for consistent pnl