# Design

## 1. Agent

- Central part of the system, manages every component
- Serve as a medium for other components to interact with each other
- Test the strategy and return trading history, backtest result, statistic.

## 2. Strategy

- A decision engine, contains logics to decide what to do next with current market data
- Query price, pending orders, filled orders, positions from Agent and return actions to perform
- Actions can be: submit orders, close orders, close positions...

## 3. Order Manager

- Manage all orders: pending, filled.
- Handle order based on their type such as: limit, market, stop...
- Add, update, delete, process order

## 4. Position Manager

- Manage all positions: long, short
- Update position based on assets price and newly filled order

## 5. Price Data

- Just a class to store kline prices and provides some utility functions to work with price

## 6. IO Device

- Incharges of handling all communication between agent and external systems/actors
- For example, it can be used to submit trading data to a queue, other actors can acess the queue and render the data
- Or it can just write data to a file, store them in database, anything is possible
- IO device is a two-way communication pipe, in can be used to receive control signals from admin, server...