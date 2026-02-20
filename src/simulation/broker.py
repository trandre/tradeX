import pandas as pd

class SimulatedBroker:
    def __init__(self, initial_purse_nok=20000):
        self.purse = initial_purse_nok
        self.positions = {} # symbol: {quantity, avg_price}
        self.history = []
        self.purse_tier = self._identify_tier(initial_purse_nok)
        
    def _identify_tier(self, amount):
        if amount <= 20000: return "SMALL (20K)"
        if amount <= 200000: return "MEDIUM (200K)"
        return "LARGE (2M)"

    def get_portfolio_value(self, current_prices):
        holdings_value = sum(
            self.positions[s]['qty'] * current_prices.get(s, 0) 
            for s in self.positions
        )
        return self.purse + holdings_value

    def execute_trade(self, symbol, quantity, price, side='buy'):
        cost = quantity * price
        # Simple simulation: 0.1% commission
        fee = cost * 0.001
        
        if side == 'buy':
            total_cost = cost + fee
            if total_cost > self.purse:
                return False, "Insufficient funds"
            self.purse -= total_cost
            self.positions[symbol] = self.positions.get(symbol, {'qty': 0, 'avg_price': 0})
            new_qty = self.positions[symbol]['qty'] + quantity
            self.positions[symbol]['avg_price'] = ((self.positions[symbol]['qty'] * self.positions[symbol]['avg_price']) + cost) / new_qty
            self.positions[symbol]['qty'] = new_qty
        
        elif side == 'sell':
            if symbol not in self.positions or self.positions[symbol]['qty'] < quantity:
                return False, "Insufficient holdings"
            gain = cost - fee
            self.purse += gain
            self.positions[symbol]['qty'] -= quantity
            if self.positions[symbol]['qty'] == 0:
                del self.positions[symbol]
                
        self.history.append({'symbol': symbol, 'side': side, 'qty': quantity, 'price': price, 'purse': self.purse})
        return True, "Success"

    def status(self, current_prices):
        val = self.get_portfolio_value(current_prices)
        return {
            "tier": self.purse_tier,
            "cash": self.purse,
            "total_value": val,
            "positions": self.positions
        }
