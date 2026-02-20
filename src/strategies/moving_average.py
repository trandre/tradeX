from src.strategies.base import BaseStrategy
import pandas as pd

class MACrossoverStrategy(BaseStrategy):
    def __init__(self, short_window=5, long_window=20):
        super().__init__("MA Crossover")
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, data):
        close = data['Close']
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
            
        short_ma = close.rolling(window=self.short_window).mean()
        long_ma = close.rolling(window=self.long_window).mean()
        
        if len(close) < self.long_window:
            return 0 # Not enough data
            
        if short_ma.iloc[-1] > long_ma.iloc[-1] and short_ma.iloc[-2] <= long_ma.iloc[-2]:
            return 1 # Buy signal
        elif short_ma.iloc[-1] < long_ma.iloc[-1] and short_ma.iloc[-2] >= long_ma.iloc[-2]:
            return -1 # Sell signal
        else:
            return 0 # Hold
