import pandas as pd
import os
from datetime import datetime, timedelta
from Strategy import Strategy
import config

class Simulator:
    def __init__(self, configFilePath=None):
        # Initialize configuration
        self.startDate = datetime.strptime(config.startDate, '%Y%m%d')
        self.endDate = datetime.strptime(config.endDate, '%Y%m%d')
        # Validate date range
        if not (datetime(2024, 6, 1) <= self.startDate <= self.endDate <= datetime(2024, 6, 30)):
            raise ValueError("Start and end dates must be between June 1, 2024, and June 30, 2024")
        self.symbols = config.symbols
        self.data_dir = '.'  # Data files are in the same folder as code
        
        # Initialize data structures
        self.df = None
        self.currentPrice = {}  # Tracks latest price per symbol
        self.netQuantity = {}  # Tracks net position per symbol
        self.buyValue = {}     # Tracks total buy value per symbol
        self.sellValue = {}    # Tracks total sell value per symbol
        self.slippage = 0.0001  # Slippage constant
        self.trade_log = []     # Store trades for analysis
        
        # Initialize strategy
        self.strategy = Strategy(self)
        
        # Run simulation
        self.readData()
        self.startSimulation()

    def readData(self):
        dfs = []
        
        # Define the specific CSV files to load
        data_files = [
            ('options_BTC_2024_06_trades.csv', 'BTC-OPTION'),
            ('futures_BTCUSD_2024_06_trades.csv', 'BTCUSD')
        ]
        
        # Load each CSV file
        for file_name, symbol in data_files:
            file_path = os.path.join(self.data_dir, file_name)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                # Rename product_symbol to Symbol for consistency
                df = df.rename(columns={'product_symbol': 'Symbol'})
                # Assign the specified symbol to the Symbol column
                df['Symbol'] = symbol
                # Convert timestamp to datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
                # Filter by date range
                df = df[(df['timestamp'] >= self.startDate) & (df['timestamp'] <= self.endDate + timedelta(days=1))]
                dfs.append(df)
                # Debug: Log price range, unique timestamps, and price distribution
                print(f"File: {file_name}, Price range: {df['price'].min():.2f} - {df['price'].max():.2f}")
                print(f"File: {file_name}, Unique timestamps: {df['timestamp'].nunique()}")
                print(f"File: {file_name}, Price std: {df['price'].std():.2f}")
                print(f"File: {file_name}, Rows after date filter: {len(df)}")
            else:
                print(f"Warning: File {file_path} not found.")
        
        # Concatenate and sort
        if dfs:
            self.df = pd.concat(dfs, ignore_index=True)
            # Sort by timestamp
            self.df = self.df.sort_values(by='timestamp').reset_index(drop=True)
            # Ensure expected columns are present
            expected_columns = ['Symbol', 'price', 'size', 'timestamp', 'buyer_role']
            self.df = self.df[expected_columns]
            # Debug: Log concatenated DataFrame info
            print(f"Concatenated DataFrame: {len(self.df)} rows, Price range: {self.df['price'].min():.2f} - {self.df['price'].max():.2f}")
            print(f"Symbols in DataFrame: {self.df['Symbol'].unique()}")
        else:
            raise ValueError("No data files found.")

    def startSimulation(self):
        for _, row in self.df.iterrows():
            symbol = row['Symbol']
            price = row['price']
            
            # Update current price
            self.currentPrice[symbol] = price
            
            # Pass market data to strategy
            self.strategy.onMarketData(row)
            
            # Periodically log P&L
            self.printPnl(row['timestamp'])

    def onOrder(self, symbol, side, quantity, price, timestamp):
        # Apply slippage
        adjusted_price = price * (1 + self.slippage) if side == 'buy' else price * (1 - self.slippage)
        
        # Calculate trade value
        trade_value = adjusted_price * quantity
        
        # Initialize tracking dictionaries if symbol not present
        if symbol not in self.netQuantity:
            self.netQuantity[symbol] = 0
            self.buyValue[symbol] = 0
            self.sellValue[symbol] = 0
        
        # Update quantities and values
        if side == 'buy':
            self.netQuantity[symbol] += quantity
            self.buyValue[symbol] += trade_value
        else:  # sell
            self.netQuantity[symbol] -= quantity
            self.sellValue[symbol] += trade_value
        
        # Log trade
        trade = {
            'timestamp': timestamp,  # Use data timestamp
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': adjusted_price,
            'trade_value': trade_value
        }
        self.trade_log.append(trade)
        
        # Notify strategy of trade confirmation
        self.strategy.onTradeConfirmation(trade)

    def printPnl(self, timestamp):
        total_pnl = 0  # Initialize total_pnl
        if self.netQuantity:  # Check if any trades exist
            for symbol in self.netQuantity:
                # Realized P&L: Total sell value - total buy value
                realized_pnl = self.sellValue[symbol] - self.buyValue[symbol]
                
                # Unrealized P&L: Current quantity * latest price
                unrealized_pnl = self.netQuantity[symbol] * self.currentPrice.get(symbol, 0)
                
                # Total P&L for symbol
                symbol_pnl = realized_pnl + unrealized_pnl
                total_pnl += symbol_pnl
        
        # Store P&L for analysis (always, for all rows)
        self.trade_log.append({
            'timestamp': timestamp,
            'total_pnl': total_pnl
        })

if __name__ == "__main__":
    simulator = Simulator()
