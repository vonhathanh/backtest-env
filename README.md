# backtest-env
- Act as API server, FE call request -> server creates a new back-test process and run with the input params

# Testing
- Run `python -m pytest` in root folder to run all unit tests
- Run `python -m pytest/file/directory` to run tests of single file
- Include `-s` to display logs

# Rules
- Submit orders: use close price
- Fill orders/close position: use open price
- Every filepath string must relative with root directory (where this README is located)

# Scripting
- Run `python -m scripts.your_script_name_without.py_extension` to run the script.
The reason is that python treats script as top-level module, it won't be able to find backtest_env
We can add hacky methods like try catch, append sys.path, install this as a module using setup.py but I don't like them
