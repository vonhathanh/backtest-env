# backtest-env
- Act as API server, FE call request -> server creates a new back-test process and run with the input params

# Decision choices
- Use close price or open price when new candle arrives?
  -> We'll use Close price because most of our strategies react based on previous candle

# Testing
- Run `python -m pytest` in root folder to run all unit tests
- Run `python -m pytest/file/directory` to run tests of single file
- Include `-s` to display logs

# Rules
- Every filepath string must relative with root directory (where this README is located)

# Scripting
- Run `python -m scripts.your_script_name_without.py_extension` to run the script.
The reason is that python treats script as top-level module, it won't be able to find backtest_env.
We can add hacky methods like try catch, append sys.path, install this as a module using setup.py but I don't like them

# TODOs
- Add stop/pause button
- Add logging functionality: order history
- Order side should be in USD, not asset quantity for consistent pnl
- Fix too many hardcoded values in unitests

# Installation
- Python >= 3.10
- Run `pip install -r requirements.txt`
- Install ruff for precommit hook and linter: `pip install ruff`
- Run `fastapi dev backtest_env/app.py` to run API server only (old command)
- Run `uvicorn backtest_env.app:socketio_app --reload` to run the server as both API and socketio endpoint