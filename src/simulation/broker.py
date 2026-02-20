import pandas as pd
import datetime

class SimulatedBroker:
    def __init__(self, initial_purse_nok=20000):
        self.initial_cash = initial_purse_nok
        self.purse = initial_purse_nok
        self.positions = {} # symbol: {qty, avg_price, category, trigger_strategy, decision_matrix, expected_horizon}
        self.history = []   
        self.total_commission = 0
        self.total_slippage = 0 # Estimert spread-kostnad
        self.daily_value_log = []
        
    def get_portfolio_value(self, current_prices):
        holdings_value = 0
        for s, pos in self.positions.items():
            price = current_prices.get(s, pos['avg_price'])
            holdings_value += pos['qty'] * price
        return self.purse + holdings_value

    def execute_trade(self, symbol, quantity, price, category="Unknown", side='buy', trigger_strategy="Manual", decision_matrix=None):
        cost = quantity * price
        
        # Realistiske kostnader
        commission = cost * 0.001 # 0.1% standard kurtasje
        slippage = cost * 0.0005  # 0.05% estimert spread/slippage
        
        self.total_commission += commission
        self.total_slippage += slippage
        
        total_fees = commission + slippage
        timestamp = datetime.datetime.now().isoformat()
        
        result = 0
        if side == 'buy':
            total_cost = cost + total_fees
            if total_cost > self.purse:
                return False, "Insufficient funds"
            self.purse -= total_cost
            
            # Sett horisont basert på strategi
            horizon = "Mellom (1-4 uker)"
            if "Medallion" in trigger_strategy: horizon = "Kort (1-5 dager)"
            if "Claude" in trigger_strategy: horizon = "Lang (3-6 mnd)"

            if symbol not in self.positions:
                self.positions[symbol] = {
                    'qty': 0, 
                    'avg_price': 0, 
                    'category': category,
                    'trigger_strategy': trigger_strategy,
                    'decision_matrix': decision_matrix or {},
                    'expected_horizon': horizon
                }
            
            pos = self.positions[symbol]
            new_qty = pos['qty'] + quantity
            pos['avg_price'] = ((pos['qty'] * pos['avg_price']) + cost) / new_qty
            pos['qty'] = new_qty
        
        elif side == 'sell':
            if symbol not in self.positions or self.positions[symbol]['qty'] < quantity:
                return False, "Insufficient holdings"
            
            pos = self.positions[symbol]
            realized_gain_loss = (price - pos['avg_price']) * quantity - total_fees
            result = realized_gain_loss
            
            self.purse += (cost - total_fees)
            pos['qty'] -= quantity
            if pos['qty'] <= 0:
                del self.positions[symbol]
                
        self.history.append({
            'timestamp': timestamp,
            'symbol': symbol, 
            'side': side, 
            'qty': quantity, 
            'price': price, 
            'result': result,
            'category': category,
            'commission': commission,
            'slippage': slippage,
            'total_fees': total_fees,
            'trigger': trigger_strategy,
            'decision_matrix': decision_matrix or {}
        })
        return True, "Success"

    def log_daily_value(self, current_prices):
        total_val = self.get_portfolio_value(current_prices)
        self.daily_value_log.append({
            'date': datetime.date.today().isoformat(),
            'total_value': total_val,
            'cash': self.purse
        })
