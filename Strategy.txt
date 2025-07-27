class Strategy:
    def __init__(self, simulator):
        self.simulator = simulator
        self.position = {}  # Tracks whether we hold a position for each symbol
        self.price_threshold = 1.0005  # Lowered to 0.05% above entry price to sell call
        self.exit_threshold = 0.9995   # Lowered to 0.05% below entry price to exit
        self.entry_price = {}  # Tracks entry price for each symbol
        self.trade_counter = {}  # Track rows since last trade per symbol

    def onMarketData(self, row):
        symbol = row['Symbol']
        price = row['price']
        size = row['size']  # Use size for dynamic quantity
        timestamp = row['timestamp']
        
        # Initialize position tracking if not already done
        if symbol not in self.position:
            self.position[symbol] = {'underlying': 0, 'option': 0}
            self.entry_price[symbol] = price
            self.trade_counter[symbol] = 0
        
        # Increment trade counter
        self.trade_counter[symbol] += 1
        
        # Debug: Log price relative to thresholds
        if symbol in self.entry_price:
            price_ratio = price / self.entry_price[symbol]
            print(f"Symbol: {symbol}, Price: {price:.2f}, Entry Price: {self.entry_price[symbol]:.2f}, "
                  f"Price/Entry: {price_ratio:.4f}, Thresholds: {self.price_threshold}/{self.exit_threshold}")
        
        # Dynamic covered call strategy
        # Buy underlying if no position, scale quantity by size
        if self.position[symbol]['underlying'] == 0:
            quantity = max(1, int(size / 100))  # Scale quantity based on size
            self.simulator.onOrder(symbol, 'buy', quantity, price, timestamp)
            self.position[symbol]['underlying'] = quantity
            self.entry_price[symbol] = price
            self.trade_counter[symbol] = 0
            print(f"Opened position: Buy {quantity} {symbol} @ {price:.2f}")
        # Sell call option if price exceeds threshold and no option sold
        elif (self.position[symbol]['underlying'] > 0 and 
              self.position[symbol]['option'] == 0 and 
              price > self.entry_price[symbol] * self.price_threshold):
            option_symbol = self._get_option_symbol(symbol)
            if option_symbol in self.simulator.currentPrice:
                quantity = self.position[symbol]['underlying']  # Match underlying quantity
                self.simulator.onOrder(option_symbol, 'sell', quantity, 
                                     self.simulator.currentPrice[option_symbol], timestamp)
                self.position[symbol]['option'] = -quantity
                self.trade_counter[symbol] = 0
                print(f"Sold option: {quantity} {option_symbol} @ {self.simulator.currentPrice[option_symbol]:.2f}")
            else:
                print(f"Failed to sell option: {option_symbol} not in currentPrice at timestamp: {timestamp}")
        # Close positions if price falls below exit threshold
        elif price < self.entry_price[symbol] * self.exit_threshold:
            if self.position[symbol]['underlying'] > 0:
                quantity = self.position[symbol]['underlying']
                self.simulator.onOrder(symbol, 'sell', quantity, price, timestamp)
                self.position[symbol]['underlying'] = 0
                print(f"Closed position: Sell {quantity} {symbol} @ {price:.2f}")
                # Reopen position to ensure continuous trading
                new_quantity = max(1, int(size / 100))
                self.simulator.onOrder(symbol, 'buy', new_quantity, price, timestamp)
                self.position[symbol]['underlying'] = new_quantity
                self.entry_price[symbol] = price
                self.trade_counter[symbol] = 0
                print(f"Reopened position: Buy {new_quantity} {symbol} @ {price:.2f}")
            if self.position[symbol]['option'] < 0:
                option_symbol = self._get_option_symbol(symbol)
                if option_symbol in self.simulator.currentPrice:
                    quantity = abs(self.position[symbol]['option'])
                    self.simulator.onOrder(option_symbol, 'buy', quantity, 
                                         self.simulator.currentPrice[option_symbol], timestamp)
                    self.position[symbol]['option'] = 0
                    self.trade_counter[symbol] = 0
                    print(f"Closed option: Buy {quantity} {option_symbol} @ "
                          f"{self.simulator.currentPrice[option_symbol]:.2f}")
                else:
                    print(f"Failed to close option: {option_symbol} not in currentPrice at timestamp: {timestamp}")
        # Periodic trade to ensure activity (every 20 rows if no trade)
        elif self.trade_counter[symbol] >= 20:
            quantity = max(1, int(size / 100))
            self.simulator.onOrder(symbol, 'buy', quantity, price, timestamp)
            self.position[symbol]['underlying'] = quantity
            self.entry_price[symbol] = price
            self.trade_counter[symbol] = 0
            print(f"Periodic trade: Buy {quantity} {symbol} @ {price:.2f}")

    def onTradeConfirmation(self, trade):
        print(f"Trade confirmed: {trade['symbol']} {trade['side']} {trade['quantity']} @ {trade['price']:.2f}")

    def _get_option_symbol(self, underlying_symbol):
        # Return BTC-OPTION for BTCUSD, else return the symbol itself
        if underlying_symbol == 'BTCUSD':
            return 'BTC-OPTION'
        return underlying_symbol
