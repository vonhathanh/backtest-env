# backtest-env
- Act as API server, FE call request -> server creates a new back-test process and run with the input params

# Testing
- Run `python -m pytest` in root folder to run all unit tests
- Run `python -m pytest/file/directory` to run tests of single file
- Include `-s` to display logs

# Rules
- Submit orders: use close price
- Fill orders/close position: use open price
